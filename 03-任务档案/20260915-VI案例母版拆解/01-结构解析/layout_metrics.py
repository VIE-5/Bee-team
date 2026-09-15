# -*- coding: utf-8 -*-
"""
VI 案例版面度量：从像素反推母版几何。

对每页测：
  1. 背景色（面积最大色）
  2. 水平结构线（跨页一致的横线 / 色块边界）的 y 位置
  3. 内容包围盒 -> 四边留白
  4. 主色 Top8

输出 <deck>_metrics.json 与 <deck>_metrics.md
"""
import os
import sys
import re
import json
from collections import Counter
from PIL import Image

W = 800            # 分析用降采样宽
DIFF = 66          # 曼哈顿色差阈值（> 视为内容）
LINE_RATIO = 0.55  # 某行内容占比超过此值 -> 结构线
EDGE_RATIO = 0.02  # 内容占比超过此值 -> 算进入内容区


def natkey(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]


def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def analyze(path):
    im = Image.open(path).convert('RGB')
    ow, oh = im.size
    nh = max(1, int(oh * W / ow))
    im = im.resize((W, nh), Image.BILINEAR)
    px = im.load()

    # 背景色：整图出现最多的颜色（量化到 8 阶降低干扰）
    q = im.quantize(colors=16, method=Image.MEDIANCUT).convert('RGB')
    qp = q.load()
    cnt = Counter(qp[x, y] for x in range(0, W, 3) for y in range(0, nh, 3))
    bg = cnt.most_common(1)[0][0]

    row_density = []
    for y in range(nh):
        c = 0
        for x in range(W):
            if dist(px[x, y], bg) > DIFF:
                c += 1
        row_density.append(c / W)

    col_density = []
    for x in range(W):
        c = 0
        for y in range(nh):
            if dist(px[x, y], bg) > DIFF:
                c += 1
        col_density.append(c / nh)

    # 内容包围盒
    top = next((y for y, d in enumerate(row_density) if d > EDGE_RATIO), None)
    bot = next((y for y in range(nh - 1, -1, -1) if row_density[y] > EDGE_RATIO), None)
    left = next((x for x, d in enumerate(col_density) if d > EDGE_RATIO), None)
    right = next((x for x in range(W - 1, -1, -1) if col_density[x] > EDGE_RATIO), None)

    # 结构线：内容占比高的连续行 -> 归组
    bands = []
    cur = None
    for y, d in enumerate(row_density):
        if d > LINE_RATIO:
            if cur is None:
                cur = [y, y]
            else:
                cur[1] = y
        else:
            if cur is not None:
                bands.append(cur)
                cur = None
    if cur:
        bands.append(cur)
    # 只保留"细带"（高度 <= 2.5% 页高）作为线；宽体当色块
    lines, blocks = [], []
    for a, b in bands:
        hh = b - a + 1
        item = (round(a / nh * 100, 1), round(b / nh * 100, 1))
        if hh <= nh * 0.025:
            lines.append(item)
        else:
            blocks.append(item)

    # 主色
    qq = im.quantize(colors=8, method=Image.MEDIANCUT).convert('RGB')
    qqp = qq.load()
    c2 = Counter(qqp[x, y] for x in range(0, W, 2) for y in range(0, nh, 2))
    palette = ['#%02X%02X%02X' % c for c, _ in c2.most_common(8)]

    im.close()
    return {
        'file': os.path.basename(path),
        'size': [ow, oh],
        'bg': '#%02X%02X%02X' % bg,
        'margins_pct': {
            'top': round(top / nh * 100, 1) if top is not None else None,
            'bottom': round((nh - 1 - bot) / nh * 100, 1) if bot is not None else None,
            'left': round(left / W * 100, 1) if left is not None else None,
            'right': round((W - 1 - right) / W * 100, 1) if right is not None else None,
        },
        'h_lines_pct': lines,
        'h_blocks_pct': blocks,
        'palette': palette,
    }


def main():
    deck_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    name = os.path.basename(deck_dir.rstrip('/\\'))
    imgs = sorted([f for f in os.listdir(deck_dir)
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))], key=natkey)
    pages = []
    for i, f in enumerate(imgs, 1):
        try:
            r = analyze(os.path.join(deck_dir, f))
            r['page'] = i
            pages.append(r)
        except Exception as e:
            print('  FAIL %s: %s' % (f, e))

    safe = re.sub(r'[\\/:*?"<>|]', '_', name)
    with open(os.path.join(out_dir, safe + '_metrics.json'), 'w', encoding='utf-8') as fh:
        json.dump(pages, fh, ensure_ascii=False, indent=1)

    # 汇总：页眉区（页高 0-15%）内最常出现的结构线位置
    hdr = Counter()
    ftr = Counter()
    for p in pages:
        for a, b in p['h_lines_pct']:
            key = '%.1f' % a
            if a < 22:
                hdr[key] += 1
            elif a > 78:
                ftr[key] += 1

    L = ['# %s — 版面度量' % name, '', '共 %d 页' % len(pages), '']
    L.append('## 页眉区（0-22%%）结构线 y 位置 Top10')
    L.append(', '.join('%s%%×%d页' % (k, v) for k, v in hdr.most_common(10)) or '（无）')
    L.append('')
    L.append('## 页脚区（78-100%%）结构线 y 位置 Top10')
    L.append(', '.join('%s%%×%d页' % (k, v) for k, v in ftr.most_common(10)) or '（无）')
    L.append('')
    L.append('## 逐页明细')
    L.append('')
    L.append('| 页 | 底色 | 内容上边距 | 内容下边距 | 左边距 | 右边距 | 结构线(y%%) |')
    L.append('|---|---|---|---|---|---|---|')
    for p in pages:
        m = p['margins_pct']
        ls = ','.join('%.1f' % a for a, _ in p['h_lines_pct'][:6]) or '-'
        L.append('| P%02d | %s | %s%% | %s%% | %s%% | %s%% | %s |' % (
            p['page'], p['bg'], m['top'], m['bottom'], m['left'], m['right'], ls))
    with open(os.path.join(out_dir, safe + '_metrics.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L))
    print('%s: %d 页' % (name, len(pages)))
    print('  页眉线一览: %s' % ', '.join('%s%%×%d' % (k, v) for k, v in hdr.most_common(6)))


if __name__ == '__main__':
    main()
