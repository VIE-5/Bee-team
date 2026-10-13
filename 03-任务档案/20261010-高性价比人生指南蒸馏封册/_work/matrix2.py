# -*- coding: utf-8 -*-
"""第二轮：定位触发幽灵页的那张 slide —— 用「复制/移除/重排」而非「改样式」"""
import re, os, time, subprocess
from pathlib import Path
import pymupdf as fitz

DECK = Path(__file__).resolve().parent.parent / "01-工蜂产出" / "T3-版式"
SRC = DECK / "index.html"
H = DECK / "_mx2.html"
P = DECK / "_mx2.pdf"
CHROME = None
for c in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          str(Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe")]:
    if Path(c).exists():
        CHROME = c
        break
PROFILE = Path.home() / "_chrome_deck_profile"
base = SRC.read_text(encoding="utf-8")
secs = re.findall(r'<section class="slide.*?</section>', base, re.S)
assert len(secs) == 43


def rebuild(new_secs):
    body = "\n".join(s.replace(' class="slide', ' class="slide', 1) for s in new_secs)
    body = body.replace(' class="slide last', ' class="slide')  # 清掉旧 last
    # 末页加 last
    body = body.replace('<section class="slide', '<section class="slide last', 1) if False else body
    parts = body.rsplit('<section class="slide', 1)
    body = parts[0] + '<section class="slide last' + parts[1].split(' class="slide', 1)[-1] if False else body
    # 简单做法：给最后一个 section 加 last
    last = new_secs[-1]
    body = "\n".join(new_secs)
    i = body.rfind('<section class="slide')
    body = body[:i] + body[i:].replace('<section class="slide', '<section class="slide last', 1)
    return re.sub(r'<body>.*?</body>', '<body>\n' + body + '\n</body>', base, flags=re.S)


VARIANTS = {
    "baseline": secs,
    "no-toc": [s for i, s in enumerate(secs) if i != 2],
    "dup-toc": secs[:3] + [secs[2]] + secs[3:],
    "toc-moved-to-end": secs[:2] + secs[3:] + [secs[2]],
    "part-before-toc": secs[:2] + [secs[3], secs[2]] + secs[4:],
    "no-preface": [s for i, s in enumerate(secs) if i != 1],
    "no-part1": [s for i, s in enumerate(secs) if i != 3],
    "dup-part1": secs[:4] + [secs[3]] + secs[4:],
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
    print(f"{tag:22s} slides={len(html.split('<section class=\"slide'))-1:2d}  pages={n:2d}  empty_pages={empt}")


for tag, ss in VARIANTS.items():
    run(tag, rebuild(ss))
