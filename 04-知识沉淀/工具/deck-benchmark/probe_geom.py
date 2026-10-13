# -*- coding: utf-8 -*-
"""版式几何探针：量版心边距 / 页眉带 / 页脚带 / 字号刻度 / 字体家族。
用法: python probe_geom.py <pdf> <page...>
数字一律以 PDF 实测为准，不读 CSS。"""
import sys, collections
import pymupdf as fitz

PDF = sys.argv[1]
PAGES = [int(x) for x in sys.argv[2:]]
doc = fitz.open(PDF)
print("PDF:", PDF, "| pages:", doc.page_count)

# ---- 全局：字号/字体统计（全部页） ----
sizes_all = collections.Counter()
fonts_all = collections.Counter()
for p in doc:
    d = p.get_text("dict")
    for b in d["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            for s in l["spans"]:
                if s["text"].strip():
                    sizes_all[round(s["size"], 1)] += len(s["text"].strip())
                    fonts_all[s["font"]] += len(s["text"].strip())
print("--- 字号刻度（pt，按字符数加权前 12）---")
for k, v in sizes_all.most_common(12):
    print("   %.1fpt  x%d 字" % (k, v))
print("--- 字体家族 ---")
for k, v in fonts_all.most_common(10):
    print("   %-42s x%d 字" % (k, v))

# ---- 逐页几何 ----
for pn in PAGES:
    if pn > doc.page_count:
        continue
    p = doc[pn - 1]
    W, H = p.rect.width, p.rect.height
    d = p.get_text("dict")
    spans = []
    for b in d["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            for s in l["spans"]:
                t = " ".join(s["text"].split())
                if not t:
                    continue
                spans.append((s["bbox"], round(s["size"], 1), s["font"], t))
    if not spans:
        print("P%02d  无文本" % pn)
        continue
    x0 = min(s[0][0] for s in spans); x1 = max(s[0][2] for s in spans)
    y0 = min(s[0][1] for s in spans); y1 = max(s[0][3] for s in spans)
    print("P%02d | 页 %.0fx%.0f | 文本 x %.1f..%.1f (左%.1f%% 右%.1f%%)  y %.1f..%.1f (上%.1f%% 下%.1f%%)"
          % (pn, W, H, x0, x1, x0 / W * 100, (W - x1) / W * 100, y0, y1, y0 / H * 100, (H - y1) / H * 100))
    top = [s for s in spans if s[0][1] < H * 0.15]
    bot = [s for s in spans if s[0][3] > H * 0.90]
    if top:
        ty0 = min(s[0][1] for s in top); ty1 = max(s[0][3] for s in top)
        print("     页眉带: y %.1f..%.1f (占高 %.1f%%, 距顶 %.1f%%)  字号 %s  例: %s"
              % (ty0, ty1, (ty1 - ty0) / H * 100, ty0 / H * 100,
                 sorted({s[1] for s in top}), top[0][3][:26]))
    if bot:
        by0 = min(s[0][1] for s in bot); by1 = max(s[0][3] for s in bot)
        print("     页脚带: y %.1f..%.1f (占高 %.1f%%, 距底 %.1f%%)  字号 %s  例: %s"
              % (by0, by1, (by1 - by0) / H * 100, (H - by1) / H * 100,
                 sorted({s[1] for s in bot}), bot[0][3][:26]))
    # 图块
    try:
        for it in p.get_image_info():
            bb = it["bbox"]
            print("     图: x %.1f..%.1f (宽%.0f, 占%.0f%%)  y %.1f..%.1f (高%.0f, 占%.0f%%)"
                  % (bb[0], bb[2], bb[2] - bb[0], (bb[2] - bb[0]) / W * 100,
                     bb[1], bb[3], bb[3] - bb[1], (bb[3] - bb[1]) / H * 100))
    except Exception:
        pass
