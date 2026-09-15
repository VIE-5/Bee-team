#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
png-color-pick.py — 无依赖 PNG 取色器（纯标准库，无需 Pillow）

用途：从设计稿/规范页/物料图里精确采样 brand color，
      避免"肉眼估色值"导致主题文件色偏。

用法：
    python png-color-pick.py <图片路径> <x,y> [<x,y> ...]
    python png-color-pick.py <图片路径> --grid 6x2          # 等分网格采样
    python png-color-pick.py <图片路径> --r 8 120,300 ...   # 指定采样半径

支持：PNG 8bit，color type 0/2/4/6（灰度/RGB/灰度A/RGBA），非隔行。
"""
import sys, zlib, struct


def read_png(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('not a PNG')
    pos, idat = 8, b''
    w = h = bd = ct = inter = None
    while pos < len(data):
        ln = struct.unpack('>I', data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        if typ == b'IHDR':
            w, h, bd, ct, _comp, _filt, inter = struct.unpack('>IIBBBBB', chunk)
        elif typ == b'IDAT':
            idat += chunk
        elif typ == b'IEND':
            break
        pos += 12 + ln
    if bd != 8 or inter != 0:
        raise ValueError('only 8bit non-interlaced PNG supported (bd=%s inter=%s)' % (bd, inter))
    ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    raw = zlib.decompress(idat)
    stride = w * ch
    out = bytearray(h * stride)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        ft = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        if ft == 1:
            for i in range(ch, stride):
                line[i] = (line[i] + line[i - ch]) & 255
        elif ft == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif ft == 3:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif ft == 4:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                b = prev[i]
                c = prev[i - ch] if i >= ch else 0
                pp = a + b - c
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, ch, out


def sample(w, h, ch, buf, x, y, r):
    rs = gs = bs = n = 0
    for yy in range(max(0, y - r), min(h, y + r + 1)):
        for xx in range(max(0, x - r), min(w, x + r + 1)):
            o = (yy * w + xx) * ch
            if ch >= 3:
                rs += buf[o]; gs += buf[o + 1]; bs += buf[o + 2]
            else:
                v = buf[o]
                rs += v; gs += v; bs += v
            n += 1
    return rs // n, gs // n, bs // n


def hexof(rgb):
    return '#%02X%02X%02X' % rgb


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    path = sys.argv[1]
    args = sys.argv[2:]
    r = 6
    if '--r' in args:
        i = args.index('--r')
        r = int(args[i + 1])
        del args[i:i + 2]

    w, h, ch, buf = read_png(path)
    print('image: %s' % path)
    print('size : %dx%d  channels=%d' % (w, h, ch))

    if args and args[0] == '--grid':
        spec = args[1] if len(args) > 1 else '6x2'
        cols, rows = [int(v) for v in spec.lower().split('x')]
        for j in range(rows):
            for i in range(cols):
                x = int((i + 0.5) * w / cols)
                y = int((j + 0.5) * h / rows)
                rgb = sample(w, h, ch, buf, x, y, r)
                print('  grid[%d,%d] (%4d,%4d)  %s  rgb%s' % (i, j, x, y, hexof(rgb), rgb))
    else:
        for a in args:
            x, y = [int(v) for v in a.split(',')]
            rgb = sample(w, h, ch, buf, x, y, r)
            print('  (%4d,%4d)  %s  rgb%s' % (x, y, hexof(rgb), rgb))


if __name__ == '__main__':
    main()
