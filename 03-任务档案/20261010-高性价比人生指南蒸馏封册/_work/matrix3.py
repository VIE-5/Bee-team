# -*- coding: utf-8 -*-
"""第三轮：把目录页的内部元素逐个摘掉，看哪个是幽灵页的引信"""
import re, os, time, subprocess
from pathlib import Path
import pymupdf as fitz

DECK = Path(__file__).resolve().parent.parent / "01-工蜂产出" / "T3-版式"
SRC = DECK / "index.html"
H = DECK / "_mx3.html"
P = DECK / "_mx3.pdf"
CHROME = None
for c in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          str(Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe")]:
    if Path(c).exists():
        CHROME = c
        break
PROFILE = Path.home() / "_chrome_deck_profile"
base = SRC.read_text(encoding="utf-8")
secs = re.findall(r'<section class="slide.*?</section>', base, re.S)
TOC = secs[2]


def css(h, extra):
    return h.replace("</style>", extra + "\n</style>", 1)


def with_toc(new_toc, extra_css=""):
    body = base.replace(TOC, new_toc, 1)
    if extra_css:
        body = css(body, extra_css)
    return body


# 取出 toc slide 内部的几个块
m_hd = re.search(r'<header class="hd">.*?</header>', TOC, re.S).group(0)
m_tocdiv = re.search(r'<div class="toc">.*?</div>(?=<footer)', TOC, re.S).group(0)
m_ft = re.search(r'<footer class="ft">.*?</footer>', TOC, re.S).group(0)
m_cols = re.search(r'<div class="toc-cols">.*?</div>\s*(?=<div class="toc-note">)', TOC, re.S).group(0)
m_col1 = re.search(r'<div class="toc-col">.*?(?=<div class="toc-col">)', m_cols, re.S).group(0)
m_note = re.search(r'<div class="toc-note">.*?</div>', TOC, re.S).group(0)

VARIANTS = {
    "baseline": base,
    "toc-div-empty": with_toc(f'<section class="slide toc-p" style="display:none">{m_hd}<div class="toc"><p style="font-size:13px">占位</p></div>{m_ft}</section>'),
    "toc-no-cols": with_toc(TOC.replace(m_cols, '', 1)),
    "toc-1col": with_toc(TOC.replace(m_cols, m_col1, 1)),
    "toc-no-note": with_toc(TOC.replace(m_note, '', 1)),
    "toc-no-hd": with_toc(TOC.replace(m_hd, '', 1)),
    "toc-cols-block": with_toc(TOC, "@media print{.toc-cols{display:block!important;}}"),
    "toc-static": with_toc(TOC, "@media print{.toc{position:static!important;top:auto!important;bottom:auto!important;left:auto!important;right:auto!important;}}"),
    "toc-div-static": with_toc(TOC, "@media print{.toc-cols{position:static!important;}}"),
    "a-to-div": with_toc(TOC.replace('<a class="toc-p">', '<div class="toc-p">').replace('<a class="toc-s">', '<div class="toc-s">').replace('</a>', '</div>'), ""),
    "toc-visible": with_toc(TOC.replace('style="display:none"', 'style="display:block"', 1)),
    "no-breakafter-2nd": css(base, "@media print{.slide.toc-p{page-break-after:auto!important;break-after:auto!important;}}"),
    "toc-fontsize-small": with_toc(TOC, "@media print{.toc *{font-size:11px!important;line-height:1.6!important;}}"),
}


def run(tag, html):
    H.write_text(html, encoding="utf-8")
    if P.exists():
        P.unlink()
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox",
           "--force-device-scale-factor=1", f"--user-data-dir={PROFILE}",
           "--no-pdf-header-footer", "--virtual-time-budget=12000",
           f"--print-to-pdf={P}", f"{H.as_uri()}?v={int(time.time()*1000)}"]
    with open(os.devnull, "wb") as nul:
        subprocess.run(cmd, stdout=nul, stderr=nul)
    doc = fitz.open(str(P))
    n = doc.page_count
    empt = [i + 1 for i in range(n) if not doc[i].get_text().strip()]
    print(f"{tag:20s} pages={n:2d}  empty={empt}")


for tag, html in VARIANTS.items():
    run(tag, html)
