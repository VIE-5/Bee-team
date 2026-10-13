# -*- coding: utf-8 -*-
"""纵向扫描 _colortest.pdf 的 P3/P4，定位目录页(蓝色 #0000FF)的分裂位置"""
from pathlib import Path
import pymupdf as fitz

DECK = Path(__file__).resolve().parent.parent / "01-工蜂产出" / "T3-版式"
doc = fitz.open(str(DECK / "_colortest.pdf"))
print("pages:", doc.page_count)

BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
CREAM = (250, 247, 242)

def runlen(page, x_frac=0.5):
    pix = page.get_pixmap(dpi=72)
    w, h = pix.width, pix.height
    x = int(w * x_frac)
    out = []
    prev = None
    for y in range(h):
        c = pix.pixel(x, y)[:3]
        # 归类
        def cls(c):
            best, bd = None, 1e9
            for name, ref in [("BLUE", BLUE), ("WHITE", WHITE), ("CREAM", CREAM)]:
                d = sum((a-b)**2 for a, b in zip(c, ref))
                if d < bd: bd, best = d, name
            return best
        k = cls(c)
        if k != prev:
            out.append((y, k, c))
            prev = k
    return out, h

for pno in (2, 3, 4):  # 0-based -> P3 P4 P5
    page = doc[pno]
    rect = page.rect
    print(f"\n=== P{pno+1} rect={rect} ===")
    segs, h = runlen(page)
    for y, k, c in segs:
        print(f"   y={y:4d}/{h} css={y/h*1123:7.1f}px  {k:6s} rgb={c}")
