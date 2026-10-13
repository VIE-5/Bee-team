# -*- coding: utf-8 -*-
"""全册对照实验：对 index.html 施加不同变换，各自导出 PDF，报告页数。
只在「全册」下复现（子集不复现），所以必须在全册上跑矩阵。
"""
import re, os, time, subprocess, sys
from pathlib import Path
import pymupdf as fitz

DECK = Path(__file__).resolve().parent.parent / "01-工蜂产出" / "T3-版式"
SRC = DECK / "index.html"
H = DECK / "_mx.html"
P = DECK / "_mx.pdf"

CHROME = None
for c in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          str(Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe")]:
    if Path(c).exists():
        CHROME = c
        break
PROFILE = Path.home() / "_chrome_deck_profile"

base = SRC.read_text(encoding="utf-8")


def css_extra(h, extra):
    return h.replace("</style>", extra + "\n</style>", 1)


VARIANTS = {
    "as-is": lambda h: h,
    "no-ws-between-slides": lambda h: h.replace("</section>\n<section", "</section><section"),
    "break-inside-avoid": lambda h: css_extra(h, "@media print{.slide{break-inside:avoid;page-break-inside:avoid;}}"),
    "print-h-1122": lambda h: css_extra(h, "@media print{.slide{height:1122px !important;}}"),
    "print-h-1118": lambda h: css_extra(h, "@media print{.slide{height:1118px !important;}}"),
    "no-ft": lambda h: re.sub(r'<footer class="ft">.*?</footer>', '', h, flags=re.S),
    "ft-static": lambda h: css_extra(h, "@media print{.ft{position:static!important;height:auto!important;}}"),
    "hide-hd": lambda h: css_extra(h, "@media print{.hd{display:none!important;}}"),
    "page-1130": lambda h: css_extra(h, "@media print{@page{size:794px 1130px;}}"),
    "page-1130-applied": None,  # 见下：需改原 @page
    "body-overflow-hidden": lambda h: css_extra(h, "@media print{html,body{overflow:hidden!important;height:auto!important;}}"),
    "slide-float-none-block": lambda h: css_extra(h, "@media print{.slide{position:static!important;height:1123px!important;}}"),
}


def run(tag, h):
    H.write_text(h, encoding="utf-8")
    if P.exists():
        P.unlink()
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox",
           "--force-device-scale-factor=1", f"--user-data-dir={PROFILE}",
           "--no-pdf-header-footer", "--virtual-time-budget=12000",
           f"--print-to-pdf={P}", f"{H.as_uri()}?v={int(time.time()*1000)}"]
    with open(os.devnull, "wb") as nul:
        subprocess.run(cmd, stdout=nul, stderr=nul)
    n = fitz.open(str(P)).page_count
    return n


for tag, fn in VARIANTS.items():
    if tag == "page-1130-applied":
        h = base.replace("@page { size: 794px 1123px; margin: 0; }", "@page { size: 794px 1130px; margin: 0; }")
    else:
        h = fn(base)
    n = run(tag, h)
    mark = "  <== 43!" if n == 43 else ("  (=44 未修复)" if n == 44 else "  ??")
    print(f"{tag:28s} pages={n}{mark}")
