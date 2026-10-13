# -*- coding: utf-8 -*-
"""幽灵页溯源：给前 N 页注入唯一底色 -> 导出 PDF -> 逐页取角像素颜色
目的：定位那多出来的一页空白，是从哪一张 slide 分裂出来的。
"""
import re, sys, subprocess, os, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECK = HERE.parent / "01-工蜂产出" / "T3-版式"
SRC = DECK / "index.html"
OUT_HTML = DECK / "_colortest.html"
OUT_PDF = DECK / "_colortest.pdf"

CHROME = None
for c in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
          str(Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe")]:
    if Path(c).exists():
        CHROME = c
        break
assert CHROME, "no chrome"
PROFILE = Path.home() / "_chrome_deck_profile"

COLORS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF",
          "#00FFFF", "#FF8000", "#8000FF", "#008000", "#000080",
          "#800000", "#808000"]

h = SRC.read_text(encoding="utf-8")

# 逐个 slide 注入 background-color（写进已有的 style="" 里）
idx = [-1]

def repl(m):
    idx[0] += 1
    i = idx[0]
    tag = m.group(0)
    if i < len(COLORS):
        if 'style="' in tag:
            tag = tag.replace('style="', f'style="background-color:{COLORS[i]} !important;', 1)
        else:
            tag = tag[:-1] + f' style="background-color:{COLORS[i]} !important">'
    return tag

h2 = re.sub(r'<section class="slide[^>]*>', repl, h)
n = idx[0] + 1
OUT_HTML.write_text(h2, encoding="utf-8")
print("slides:", n)

if OUT_PDF.exists():
    OUT_PDF.unlink()
cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox",
       "--force-device-scale-factor=1", f"--user-data-dir={PROFILE}",
       "--no-pdf-header-footer", "--virtual-time-budget=20000",
       f"--print-to-pdf={OUT_PDF}", f"{OUT_HTML.as_uri()}?v={int(time.time()*1000)}"]
with open(os.devnull, "wb") as nul:
    subprocess.run(cmd, stdout=nul, stderr=nul)
print("pdf exists:", OUT_PDF.exists(), OUT_PDF.stat().st_size if OUT_PDF.exists() else 0)

import fitz
doc = fitz.open(str(OUT_PDF))
print("PDF physical pages:", doc.page_count)
CMAP = {}
for i, c in enumerate(COLORS):
    CMAP[(int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16))] = i

def nearest(rgb):
    best, bd = None, 1e9
    for c, i in CMAP.items():
        d = sum((a - b) ** 2 for a, b in zip(rgb, c))
        if d < bd:
            bd, best = d, i
    return best, bd

for pno in range(doc.page_count):
    page = doc[pno]
    pix = page.get_pixmap(dpi=36)  # 36dpi -> 397x561
    w, hh = pix.width, pix.height
    def px(x, y):
        return pix.pixel(x, y)[:3]
    corners = {
        "TL": px(1, 1), "TR": px(w - 2, 1), "BL": px(1, hh - 2), "BR": px(w - 2, hh - 2),
        "top20": px(w // 2, max(1, int(hh * 0.02))), "top8": px(w // 2, max(1, int(hh * 0.02))),
    }
    s = " ".join(f"{k}={v}" for k, v in corners.items())
    c0, d0 = nearest(corners["TL"])
    c1, d1 = nearest(corners["TR"])
    tag = ""
    if pno < 12:
        tag = f"  -> TL~slide{c0}(d={d0}) TR~slide{c1}(d={d1})"
    print(f"P{pno+1:02d} {s}{tag}")
