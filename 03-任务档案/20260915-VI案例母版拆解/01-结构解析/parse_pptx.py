# -*- coding: utf-8 -*-
"""
VI 案例 PPTX 结构解析器（零依赖，纯标准库）
用途：把 PPTX 每页的每个元素量化成坐标/尺寸/占位符/字号/色值，
     用于反推「母版」——页眉页脚、板块切分、图文版式规律。

输出：
  <name>.json       结构化全量数据
  <name>.md         人类可读摘要
"""
import zipfile
import xml.etree.ElementTree as ET
import json
import os
import sys
from collections import Counter

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKGREL = 'http://schemas.openxmlformats.org/package/2006/relationships'

EMU_IN = 914400.0
EMU_PT = 12700.0


def q(tag, ns_prefix):
    return '{%s}%s' % ({'a': A, 'p': P, 'r': R, 'pr': PKGREL}[ns_prefix], tag)


def slide_size(z):
    """返回 (w_emu, h_emu)"""
    with z.open('ppt/presentation.xml') as f:
        root = ET.fromstring(f.read())
    s = root.find(q('sldSz', 'p'))
    return int(s.get('cx')), int(s.get('cy'))


def ordered_slides(z):
    """按 presentation.xml 的 sldIdLst 顺序返回 slide 路径列表"""
    with z.open('ppt/_rels/presentation.xml.rels') as f:
        root = ET.fromstring(f.read())
    rels = {}
    for rel in root:
        rels[rel.get('Id')] = rel.get('Target')
    out = []
    with z.open('ppt/presentation.xml') as f:
        root = ET.fromstring(f.read())
    lst = root.find(q('sldIdLst', 'p'))
    if lst is None:
        return out
    for sld in lst:
        rid = sld.get(q('id', 'r'))
        tgt = rels.get(rid, '')
        tgt = tgt.replace('../', '')
        out.append('ppt/' + tgt if not tgt.startswith('ppt/') else tgt)
    return out


def xfrm_of(el):
    """从 spPr/grpSpPr 取 off+ext"""
    spPr = el.find(q('spPr', 'p'))
    if spPr is None:
        spPr = el.find(q('grpSpPr', 'p'))
    if spPr is None:
        return None
    x = spPr.find(q('xfrm', 'a'))
    if x is None:
        return None
    off = x.find(q('off', 'a'))
    ext = x.find(q('ext', 'a'))
    if off is None or ext is None:
        return None
    return (int(off.get('x')), int(off.get('y')),
            int(ext.get('cx')), int(ext.get('cy')))


def placeholder_of(el):
    nv = el.find(q('nvSpPr', 'p')) or el.find(q('nvPicPr', 'p')) or el.find(q('nvGraphicFramePr', 'p')) or el.find(q('nvGrpSpPr', 'p'))
    if nv is None:
        return None, None
    cNv = nv.find(q('cNvPr', 'p'))
    nm = cNv.get('name') if cNv is not None else None
    nvPr = nv.find(q('nvPr', 'p'))
    pht = None
    if nvPr is not None:
        ph = nvPr.find(q('ph', 'p'))
        if ph is not None:
            pht = ph.get('type') or 'body'
    return nm, pht


def texts_and_style(el):
    """收集所有 a:t 文本、字号集合、色值列表"""
    txts, sizes, colors = [], Counter(), Counter()
    for t in el.iter(q('t', 'a')):
        if t.text:
            txts.append(t.text)
    for rPr in el.iter(q('rPr', 'a')):
        sz = rPr.get('sz')
        if sz:
            sizes[int(sz) // 100] += 1
    for c in el.iter(q('srgbClr', 'a')):
        v = c.get('val')
        if v:
            colors['#' + v.upper()] += 1
    for c in el.iter(q('schemeClr', 'a')):
        v = c.get('val')
        if v:
            colors['@' + v] += 1
    return ''.join(txts).strip(), sizes, colors


def shape_fill(el):
    """取形状填充色"""
    spPr = el.find(q('spPr', 'p'))
    if spPr is None:
        return None
    for tag in ('solidFill', 'gradFill', 'noFill'):
        n = spPr.find(q(tag, 'a'))
        if n is None:
            continue
        if tag == 'noFill':
            return 'none'
        if tag == 'gradFill':
            cs = [c.get('val') for c in n.iter(q('srgbClr', 'a'))]
            return 'grad:' + '/'.join(['#' + c.upper() for c in cs if c])
        c = n.find(q('srgbClr', 'a'))
        if c is not None:
            return '#' + c.get('val').upper()
        c = n.find(q('schemeClr', 'a'))
        if c is not None:
            return '@' + c.get('val')
        return 'other'
    return None


def prst_geom(el):
    g = el.find('.//' + q('prstGeom', 'a'))
    if g is not None:
        return g.get('prst')
    return None


def walk(spTree, rels_map, depth=0):
    """递归遍历形状树"""
    out = []
    for el in spTree:
        if el.tag.endswith('}sp'):
            nm, ph = placeholder_of(el)
            txt, sizes, colors = texts_and_style(el)
            rec = {
                'kind': 'text' if txt else 'shape',
                'name': nm,
                'ph': ph,
                'geom': prst_geom(el),
                'fill': shape_fill(el),
                'bbox': xfrm_of(el),
                'text': txt[:120],
                'text_len': len(txt),
                'sizes': dict(sizes),
                'colors': dict(colors),
                'depth': depth,
            }
            out.append(rec)
        elif el.tag.endswith('}pic'):
            nm, ph = placeholder_of(el)
            blip = el.find('.//' + q('blip', 'a'))
            rid = blip.get(q('embed', 'r')) if blip is not None else None
            rec = {
                'kind': 'pic',
                'name': nm,
                'ph': ph,
                'bbox': xfrm_of(el),
                'rel': rid,
                'target': rels_map.get(rid),
                'depth': depth,
            }
            out.append(rec)
        elif el.tag.endswith('}graphicFrame'):
            nm, ph = placeholder_of(el)
            gd = el.find('.//' + q('graphicData', 'a'))
            uri = gd.get('uri') if gd is not None else ''
            rec = {
                'kind': 'table' if 'table' in uri else ('chart' if 'chart' in uri else 'graphic'),
                'name': nm,
                'ph': ph,
                'bbox': xfrm_of(el),
                'depth': depth,
            }
            out.append(rec)
        elif el.tag.endswith('}grpSp'):
            nm, ph = placeholder_of(el)
            sub = walk(el.find(q('spTree', 'p')), rels_map, depth + 1) if el.find(q('spTree', 'p')) is not None else []
            out.append({
                'kind': 'group',
                'name': nm,
                'ph': ph,
                'bbox': xfrm_of(el),
                'children': sub,
                'depth': depth,
            })
            out.append({'__group_marker__': True, 'children': sub})
    # 过滤 marker
    return [r for r in out if not r.get('__group_marker__')]


def rels_for(z, path):
    """读某个 slide 的 rels"""
    d, f = os.path.split(path)
    rp = d + '/_rels/' + f + '.rels'
    rels = {}
    try:
        with z.open(rp) as fh:
            root = ET.fromstring(fh.read())
        for rel in root:
            rels[rel.get('Id')] = rel.get('Target')
    except KeyError:
        pass
    return rels


def flatten(shapes):
    out = []
    for s in shapes:
        out.append(s)
        for c in s.get('children', []):
            out.extend(flatten([c]))
    return out


def parse(path):
    name = os.path.splitext(os.path.basename(path))[0]
    z = zipfile.ZipFile(path)
    sw, sh = slide_size(z)
    slides = ordered_slides(z)

    # 母版 / 版式信息
    masters = [n for n in z.namelist() if n.startswith('ppt/slideMasters/slideMaster')]
    layouts = [n for n in z.namelist() if n.startswith('ppt/slideLayouts/slideLayout')]
    theme = [n for n in z.namelist() if 'theme' in n and n.endswith('.xml')]

    # 全局色值统计
    palette = Counter()
    for n in theme + masters:
        try:
            with z.open(n) as f:
                root = ET.fromstring(f.read())
            for c in root.iter(q('srgbClr', 'a')):
                v = c.get('val')
                if v:
                    palette['#' + v.upper()] += 1
        except Exception:
            pass

    pages = []
    for idx, sp in enumerate(slides, 1):
        try:
            with z.open(sp) as f:
                root = ET.fromstring(f.read())
        except KeyError:
            continue
        rm = rels_for(z, sp)
        tree = root.find(q('cSld', 'p')).find(q('spTree', 'p'))
        shapes = walk(tree, rm)
        flat = flatten(shapes)
        imgs = [s for s in flat if s['kind'] == 'pic']
        txts = [s for s in flat if s['kind'] == 'text']
        # 占位符分类
        phs = [(s.get('ph'), s.get('name')) for s in flat if s.get('ph')]
        pages.append({
            'index': idx,
            'shapes_total': len(flat),
            'img_count': len(imgs),
            'text_count': len(txts),
            'ph': phs,
            'shapes': flat,
        })

    data = {
        'file': os.path.basename(path),
        'name': name,
        'slide_size_emu': [sw, sh],
        'slide_size_pt': [round(sw / EMU_PT, 1), round(sh / EMU_PT, 1)],
        'slide_ratio': round(sw / sh, 4),
        'page_count': len(pages),
        'master_count': len(masters),
        'layout_count': len(layouts),
        'palette': palette.most_common(40),
        'pages': pages,
    }
    z.close()
    return data


def fmt_bbox(b, sw, sh):
    if not b:
        return '-'
    x, y, cx, cy = b
    return 'x%.1f%% y%.1f%% w%.1f%% h%.1f%%' % (
        x / sw * 100, y / sh * 100, cx / sw * 100, cy / sh * 100)


def to_md(d):
    L = []
    L.append('# %s' % d['name'])
    L.append('')
    L.append('- 画布: %s pt × %s pt  (比例 %.4f)' % (d['slide_size_pt'][0], d['slide_size_pt'][1], d['slide_ratio']))
    L.append('- 页数: %d ｜ 母版 %d ｜ 版式 %d' % (d['page_count'], d['master_count'], d['layout_count']))
    L.append('- 主题色 Top15: ' + ', '.join('%s×%d' % (c, n) for c, n in d['palette'][:15]))
    L.append('')
    sw, sh = d['slide_size_emu']
    for pg in d['pages']:
        L.append('## P%02d  (形状 %d ｜ 图 %d ｜ 文 %d)' % (pg['index'], pg['shapes_total'], pg['img_count'], pg['text_count']))
        for s in pg['shapes']:
            if s.get('kind') == 'group':
                L.append('- [组] %s  bbox=%s  子元素%d' % (s.get('name'), fmt_bbox(s.get('bbox'), sw, sh), len(s.get('children', []))))
                continue
            extra = ''
            if s.get('kind') == 'text':
                sz = sorted(s['sizes'].items(), key=lambda kv: -kv[1])[:3]
                extra = ' sz=%s' % (sz,)
            if s.get('kind') == 'pic':
                extra = ' -> %s' % s.get('target')
            ph = s.get('ph')
            phs = '[PH:%s] ' % ph if ph else ''
            L.append('- %s%s%s  bbox=%s%s%s' % (
                phs, s.get('kind'), (' "' + s.get('name') + '"') if s.get('name') else '',
                fmt_bbox(s.get('bbox'), sw, sh),
                extra,
                ('  «' + s['text'][:56] + '»') if s.get('text') else ''))
        L.append('')
    return '\n'.join(L)


def main():
    src_dir = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    files = sorted([f for f in os.listdir(src_dir) if f.lower().endswith('.pptx')])
    summary = []
    for f in files:
        p = os.path.join(src_dir, f)
        try:
            d = parse(p)
        except Exception as e:
            print('FAIL %s: %s' % (f, e))
            continue
        base = os.path.splitext(f)[0]
        with open(os.path.join(out_dir, base + '.json'), 'w', encoding='utf-8') as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
        with open(os.path.join(out_dir, base + '.md'), 'w', encoding='utf-8') as fh:
            fh.write(to_md(d))
        summary.append((base, d['page_count'], d['slide_size_pt'], d['slide_ratio'], len(d['palette'])))
        print('OK  %-40s %3d页  %s  ratio=%.4f' % (base, d['page_count'], d['slide_size_pt'], d['slide_ratio']))
    print('\n=== 汇总 ===')
    for s in summary:
        print('%-40s %3d页' % (s[0], s[1]))


if __name__ == '__main__':
    main()
