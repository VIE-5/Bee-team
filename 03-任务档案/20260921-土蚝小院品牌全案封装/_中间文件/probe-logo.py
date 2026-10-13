# -*- coding: utf-8 -*-
"""探测 logo-白.png 的像素层次：是否纯墨平涂还是有自然笔触层次。"""
from collections import Counter
from pathlib import Path

from PIL import Image

p = Path(r"E:\唐V-work\土蚝小院\土蚝\LOGO定\土蚝小院视觉资产\logo-白.png")
im = Image.open(p).convert("RGBA")
print("size", im.size, "mode", im.mode)

px = im.load()
w, h = im.size
cnt = Counter()
tot = vis = 0
for y in range(0, h, 3):
    for x in range(0, w, 3):
        r, g, b, a = px[x, y]
        tot += 1
        if a < 60:
            continue
        vis += 1
        cnt[(r // 24 * 24, g // 24 * 24, b // 24 * 24)] += 1

print("visible ratio %.2f%%" % (vis * 100 / tot))
for c, n in cnt.most_common(12):
    print("   ", c, n)

# alpha 分布（笔触边缘柔度）
ac = Counter()
for y in range(0, h, 3):
    for x in range(0, w, 3):
        a = px[x, y][3]
        ac[a // 32 * 32] += 1
print("alpha histogram (bucket:count):")
for k in sorted(ac):
    print("   %3d : %d" % (k, ac[k]))

bb = im.split()[-1].getbbox()
print("alpha bbox", bb, "-> crop", (bb[2] - bb[0], bb[3] - bb[1]))
