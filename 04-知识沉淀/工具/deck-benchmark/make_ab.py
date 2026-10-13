# -*- coding: utf-8 -*-
"""A/B 并置对照图生成器：左 A 右 B，带 ASCII 标签行。用于对标报告的可视证据。

用法:
    python make_ab.py <A.pdf> <B.pdf> <out.png> <A页码> <B页码> "<左标签>" "<右标签>"

例:
    python make_ab.py a.pdf b.pdf out.png 11 6 "A P11 / logo variants" "B P06 / logo spec"

注意:
    - 标签走内置 helv 字体，**只支持 ASCII**；中文会渲染成空白
    - 输出 2430×828 级别大图属正常，md5 应各不相同（相同即说明内容没换）
"""
import sys
import pymupdf as fitz

if len(sys.argv) < 8:
    print(__doc__)
    sys.exit(1)

PA, PB, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
PA_PG, PB_PG = int(sys.argv[4]), int(sys.argv[5])
L1, L2 = sys.argv[6], sys.argv[7]

Z = 1.15
GAP, PAD, LBL = 24, 30, 34

da, db = fitz.open(PA), fitz.open(PB)
pa = da[PA_PG - 1].get_pixmap(matrix=fitz.Matrix(Z, Z))
pb = db[PB_PG - 1].get_pixmap(matrix=fitz.Matrix(Z, Z))

Wp = PAD * 2 + pa.width + GAP + pb.width
Hp = PAD * 2 + LBL + pa.height
doc = fitz.open()
pg = doc.new_page(width=Wp, height=Hp)
pg.draw_rect(fitz.Rect(0, 0, Wp, Hp), color=None, fill=(0.945, 0.941, 0.929))

r1 = fitz.Rect(PAD, PAD + LBL, PAD + pa.width, PAD + LBL + pa.height)
r2 = fitz.Rect(PAD + pa.width + GAP, PAD + LBL,
               PAD + pa.width + GAP + pb.width, PAD + LBL + pb.height)

pg.insert_text((PAD, PAD + 18), L1, fontsize=19, fontname="hebo", color=(0.11, 0.11, 0.11))
pg.insert_text((r2.x0, PAD + 18), L2, fontsize=19, fontname="hebo", color=(0.72, 0.15, 0.15))
pg.insert_image(r1, pixmap=pa)
pg.insert_image(r2, pixmap=pb)
pg.draw_rect(r1, color=(0.75, 0.75, 0.72), width=0.8)
pg.draw_rect(r2, color=(0.75, 0.75, 0.72), width=0.8)

doc.save(OUT)
print("saved %s  %.0fx%.0f" % (OUT, Wp, Hp))
