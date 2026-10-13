# -*- coding: utf-8 -*-
"""V6 结构拆解：逐页取「页型分类 + 标题层 + 图像块」，两版 PDF 并排比对。"""
import pymupdf, pathlib, json, re

ROOT = pathlib.Path(r"E:\唐V-work\土蚝小院")
TARGETS = [("v6(用户指定)", ROOT / "土蚝小院-品牌视觉全案-v6.pdf"),
           ("index(源目录)", ROOT / "品牌视觉资产封装" / "index.pdf")]


def lines_of(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b.get("lines", []):
            txt = "".join(s["text"] for s in l["spans"]).strip()
            if not txt:
                continue
            sz = max(round(s["size"], 1) for s in l["spans"])
            out.append((round(l["bbox"][1], 1), round(l["bbox"][0], 1), sz, txt))
    out.sort()
    return out


dumps = {}
for tag, path in TARGETS:
    d = pymupdf.open(path)
    pages = []
    for p in d:
        ls = lines_of(p)
        r = p.rect
        pages.append({"rect": (round(r.width, 2), round(r.height, 2)),
                      "n_lines": len(ls),
                      "n_img": len(p.get_images(full=True)),
                      "lines": ls})
    dumps[tag] = pages
    print("%-14s 页数=%d  MediaBox=%s" % (tag, len(pages), pages[0]["rect"]))

# 结构指纹：每页的 (图像数, 行数, 最大字号文本)
def fp(pages):
    sig = []
    for p in pages:
        big = max(p["lines"], key=lambda t: t[2]) if p["lines"] else None
        sig.append((p["n_img"], p["n_lines"], (big[3][:18] if big else ""), (big[2] if big else 0)))
    return sig

a, b = fp(dumps["v6(用户指定)"]), fp(dumps["index(源目录)"])
if len(a) != len(b):
    print("!! 页数不同")
else:
    diff = [i + 1 for i, (x, y) in enumerate(zip(a, b)) if x != y]
    print("结构指纹差异页:", diff if diff else "无（两版结构一致）")

pathlib.Path("_v6dump.json").write_text(
    json.dumps({k: v for k, v in dumps.items()}, ensure_ascii=False), encoding="utf-8")
print("dump -> _v6dump.json")
