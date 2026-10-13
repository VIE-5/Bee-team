# -*- coding: utf-8 -*-
"""A/B 并置对照图：左=土蚝V6，右=碗香。用于报告可视证据。"""
import pymupdf as fitz

T = r"E:/唐V-work/土蚝小院/土蚝小院-品牌视觉全案-v6.pdf"
W = r"D:/WORK——Vie/贵州遵义/邓总-VI/沃克/品牌全案封装/01-工蜂产出/碗香-品牌全案封装.pdf"
dt, dw = fitz.open(T), fitz.open(W)
Z = 1.15
GAP, PAD, LBL = 24, 30, 34

def pair(tp, wp, out, l1, l2):
    pa = dt[tp - 1].get_pixmap(matrix=fitz.Matrix(Z, Z))
    pb = dw[wp - 1].get_pixmap(matrix=fitz.Matrix(Z, Z))
    Wp = PAD * 2 + pa.width + GAP + pb.width
    Hp = PAD * 2 + LBL + pa.height
    doc = fitz.open()
    pg = doc.new_page(width=Wp, height=Hp)
    pg.draw_rect(fitz.Rect(0, 0, Wp, Hp), color=None, fill=(0.945, 0.941, 0.929))
    r1 = fitz.Rect(PAD, PAD + LBL, PAD + pa.width, PAD + LBL + pa.height)
    r2 = fitz.Rect(PAD + pa.width + GAP, PAD + LBL, PAD + pa.width + GAP + pb.width, PAD + LBL + pb.height)
    pg.insert_text((PAD, PAD + 18), l1, fontsize=19, fontname="hebo", color=(0.11, 0.11, 0.11))
    pg.insert_text((r2.x0, PAD + 18), l2, fontsize=19, fontname="hebo", color=(0.72, 0.15, 0.15))
    pg.insert_image(r1, pixmap=pa)
    pg.insert_image(r2, pixmap=pb)
    pg.draw_rect(r1, color=(0.75, 0.75, 0.72), width=0.8)
    pg.draw_rect(r2, color=(0.75, 0.75, 0.72), width=0.8)
    doc.save(out)
    print("saved", out, "%.0fx%.0f" % (Wp, Hp))

pair(19, 21, "_AB-1-material-page.png", "TUHAO V6  P19  /  material page", "WANXIANG  P21  /  material page")
pair(11, 6, "_AB-2-logo-spec.png", "TUHAO V6  P11  /  logo variants", "WANXIANG  P06  /  logo spec")
pair(3, 4, "_AB-3-divider.png", "TUHAO V6  P03  /  section divider", "WANXIANG  P04  /  part opener")
