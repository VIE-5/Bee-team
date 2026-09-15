# -*- coding: utf-8 -*-
"""
从 VI 案例 PPTX 中提取设计稿原图 + 探测像素尺寸（零依赖，纯标准库）

这些案例是「一页一图」图册型 PPT，每页一张满幅设计稿，
所以版式信息只能从图片像素里读。
"""
import zipfile
import os
import sys
import struct
import re


def png_size(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    w, h = struct.unpack('>II', data[16:24])
    return w, h


def jpeg_size(data):
    if data[:2] != b'\xff\xd8':
        return None
    i = 2
    n = len(data)
    while i < n - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        m = data[i + 1]
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        if i + 4 > n:
            break
        seglen = struct.unpack('>H', data[i + 2:i + 4])[0]
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack('>HH', data[i + 5:i + 9])
            return w, h
        i += 2 + seglen
    return None


def gif_size(data):
    if data[:6] not in (b'GIF87a', b'GIF89a'):
        return None
    w, h = struct.unpack('<HH', data[6:10])
    return w, h


def img_size(data):
    for fn in (png_size, jpeg_size, gif_size):
        try:
            r = fn(data)
        except Exception:
            r = None
        if r:
            return r
    return None


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]


def main():
    src_dir, out_root = sys.argv[1], sys.argv[2]
    files = sorted([f for f in os.listdir(src_dir) if f.lower().endswith('.pptx')])
    report = []
    for f in files:
        deck = os.path.splitext(f)[0]
        safe = re.sub(r'[\\/:*?"<>|]', '_', deck)
        out = os.path.join(out_root, safe)
        os.makedirs(out, exist_ok=True)
        z = zipfile.ZipFile(os.path.join(src_dir, f))
        media = [n for n in z.namelist()
                 if n.startswith('ppt/media/') and not n.endswith('/')]
        media.sort(key=natural_key)
        # 建立 slide -> media 序号映射（保证页序正确）
        rows = []
        for n in media:
            data = z.read(n)
            sz = img_size(data)
            root, ext = os.path.splitext(os.path.basename(n))
            dst = os.path.join(out, root + ext.lower())
            with open(dst, 'wb') as fh:
                fh.write(data)
            rows.append((os.path.basename(n), sz, len(data)))
        z.close()
        report.append((deck, len(media), rows))
        print('=== %s : media %d 个 ===' % (deck, len(media)))
        for nm, sz, ln in rows[:6]:
            print('   %-16s %s  %.0f KB' % (nm, ('%dx%d' % sz) if sz else '?', ln / 1024))
        if len(rows) > 6:
            print('   ... 共 %d 个' % len(rows))
        # 尺寸分布
        cnt = {}
        for _, sz, _ in rows:
            k = '%dx%d' % sz if sz else 'unknown'
            cnt[k] = cnt.get(k, 0) + 1
        print('   尺寸分布: %s' % ', '.join('%s×%d' % (k, v) for k, v in sorted(cnt.items(), key=lambda kv: -kv[1])[:5]))
        print('')
    print('=== 总计 %d 个 deck，%d 张图 ===' % (len(report), sum(r[1] for r in report)))


if __name__ == '__main__':
    main()
