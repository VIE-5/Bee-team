# -*- coding: utf-8 -*-
"""从 PDF 本体取证：页数/MediaBox/文本层/图像块 -> 还原结构与页型。不借道缩略图。"""
import sys, json, collections
import pymupdf as fitz

PDF = sys.argv[1]
doc = fitz.open(PDF)
n = doc.page_count
print("PDF:", PDF)
print("pages:", n)

# ---- 1. 几何 ----
sizes = collections.Counter()
for p in doc:
    r = p.rect
    sizes[(round(r.width, 2), round(r.height, 2))] += 1
print("--- MediaBox 尺寸集合 ---")
for k, v in sizes.items():
    print("  %.2f x %.2f pt  = %.4f 比例  -> %d 页" % (k[0], k[1], k[0] / k[1], v))

# ---- 2. 页眉/页脚带内文本 ----
print("--- 每页结构 ---")
rows = []
for i, p in enumerate(doc, 1):
    H = p.rect.height
    W = p.rect.width
    blocks = p.get_text("blocks")  # x0,y0,x1,y1,text,block_no,block_type
    hdr, ftr, body = [], [], []
    for b in blocks:
        if b[6] != 0:
            continue
        t = " ".join(b[4].split())
        if not t:
            continue
        y0, y1 = b[1], b[3]
        if y0 < H * 0.13:
            hdr.append(t)
        elif y1 > H * 0.92:
            ftr.append(t)
        else:
            body.append(t)
    # 图像
    try:
        infos = p.get_image_info()
    except Exception:
        infos = []
    imgs = []
    for it in infos:
        bb = it["bbox"]
        imgs.append((round(bb[2] - bb[0]), round(bb[3] - bb[1])))
    full_bleed = 0
    for w, h in imgs:
        if w >= W * 0.92 and h >= H * 0.92:
            full_bleed += 1
    txt_all = p.get_text("text")
    rows.append({
        "pg": i, "hdr": hdr, "ftr": ftr,
        "n_txt_chars": len(txt_all.strip()),
        "n_blocks": len(body), "n_img": len(infos),
        "img_max": max([w for w, h in imgs], default=0),
        "full_bleed": full_bleed,
        "body_head": (body[0][:38] if body else ""),
    })

for r in rows:
    print("P%02d | hdr=%s | ftr=%s | 字%4d 块%2d 图%2d 图max%4d 满幅%d | %s"
          % (r["pg"], ("|".join(r["hdr"]))[:34], ("|".join(r["ftr"]))[:16],
             r["n_txt_chars"], r["n_blocks"], r["n_img"], r["img_max"],
             r["full_bleed"], r["body_head"]))

with open(PDF + ".probe.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)
print("saved:", PDF + ".probe.json")
