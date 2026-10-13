# -*- coding: utf-8 -*-
"""块级布局探针：按 y 序列出每页所有文本块 bbox + 文本，以及图片 bbox。
用于还原单页布局骨架（上图下文 / 左文右图 / 纯图页）。
用法: python probe_blocks.py <pdf> <page...>"""
import sys
import pymupdf as fitz

PDF = sys.argv[1]
PAGES = [int(x) for x in sys.argv[2:]]
doc = fitz.open(PDF)
print("PDF:", PDF)

for pn in PAGES:
    if pn > doc.page_count:
        continue
    p = doc[pn - 1]
    W, H = p.rect.width, p.rect.height
    print("\n===== P%02d  (%.0fx%.0f) =====" % (pn, W, H))
    items = []
    for b in p.get_text("blocks"):
        if b[6] != 0:
            continue
        t = " ".join(b[4].split())
        if not t:
            continue
        items.append(("T", b[0], b[1], b[2], b[3], t))
    for it in p.get_image_info():
        bb = it["bbox"]
        items.append(("I", bb[0], bb[1], bb[2], bb[3],
                      "<img %dx%d>" % (it.get("width", 0), it.get("height", 0))))
    for kind, x0, y0, x1, y1, t in sorted(items, key=lambda a: (a[2], a[1])):
        print("  %s x %6.1f..%6.1f (%4.1f%%~%4.1f%%)  y %6.1f..%6.1f (%4.1f%%~%4.1f%%)  %s"
              % (kind, x0, x1, x0 / W * 100, x1 / W * 100,
                 y0, y1, y0 / H * 100, y1 / H * 100, t[:64]))
