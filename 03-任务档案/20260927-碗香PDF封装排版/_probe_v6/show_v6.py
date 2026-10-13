# -*- coding: utf-8 -*-
"""按页打印 V6 结构：页型推断 + 标题层 + 图块 + 页眉栏目。"""
import json, pathlib

d = json.loads(pathlib.Path("_v6dump.json").read_text(encoding="utf-8"))
pages = d["v6(用户指定)"]
probe = json.loads(pathlib.Path(
    r"E:\唐V-work\土蚝小院\土蚝小院-品牌视觉全案-v6.pdf.probe.json").read_text(encoding="utf-8"))

for i, p in enumerate(pages):
    pg = i + 1
    ls = p["lines"]
    # 页眉带 y<64 / 页脚带 y>573（画布 638pt，头 10% 尾 7%）
    hdr = [t for t in ls if t[0] < 64]
    ftr = [t for t in ls if t[0] > 560]
    body = [t for t in ls if 64 <= t[0] <= 560]
    body.sort(key=lambda t: -t[2])
    big = body[:3]
    hd = " | ".join(x[3] for x in hdr)[:46]
    ft = " | ".join(x[3] for x in ftr)[:34]
    bo = " / ".join("%.1f %s" % (x[2], x[3][:22]) for x in big)
    print("P%02d img=%d ln=%2d  hdr[%s]  ft[%s]" % (pg, p["n_img"], p["n_lines"], hd, ft))
    if bo:
        print("      body: %s" % bo)
