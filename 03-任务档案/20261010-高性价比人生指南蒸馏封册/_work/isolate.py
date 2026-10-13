# -*- coding: utf-8 -*-
"""二分隔离：只保留指定 slide，导出 PDF，报告页数与每页颜色/几何。
用法: python isolate.py 1 2      # 只留 preface + toc
"""
import re, os, sys, time, subprocess
from pathlib import Path
import pymupdf as fitz

DECK = Path(__file__).resolve().parent.parent / "01-工蜂产出" / "T3-版式"
SRC = DECK / "index.html"
W = DECK / "_iso.html"
P = DECK / "_iso.pdf"

CHROME = None
for c in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
          str(Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe")]:
    if Path(c).exists():
        CHROME = c
        break
PROFILE = Path.home() / "_chrome_deck_profile"

COLORS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]

h = SRC.read_text(encoding="utf-8")
# 切出 <section ...>...</section> 序列
secs = re.findall(r'<section class="slide.*?</section>', h, re.S)
assert len(secs) == 43, len(secs)

keep = [int(x) for x in sys.argv[1:]]
picked = []
for n, i in enumerate(keep):
    s = secs[i]
    s = s.replace(' class="slide', f' class="slide iso-{n}"', 1)
    if 'style="' in s.split('>')[0]:
        s = s.replace('style="', f'style="background-color:{COLORS[n % 6]} !important;', 1)
    # 末页加 last
    if n == len(keep) - 1:
        s = s.replace('<section class="slide', '<section class="slide last', 1)
    picked.append(s)

body = "\n".join(picked)
out = re.sub(r'<body>.*?</body>', '<body>\n' + body + '\n</body>', h, flags=re.S)
W.write_text(out, encoding="utf-8")

if P.exists():
    P.unlink()
cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox",
       "--force-device-scale-factor=1", f"--user-data-dir={PROFILE}",
       "--no-pdf-header-footer", "--virtual-time-budget=15000",
       f"--print-to-pdf={P}", f"{W.as_uri()}?v={int(time.time()*1000)}"]
with open(os.devnull, "wb") as nul:
    subprocess.run(cmd, stdout=nul, stderr=nul)

doc = fitz.open(str(P))
def cls(c):
    refs = [((255,0,0),"R"),((0,255,0),"G"),((0,0,255),"B"),((255,255,0),"Y"),
            ((255,0,255),"M"),((0,255,255),"C"),((255,255,255),"W"),((250,247,242),"cream")]
    best,bd=None,1e9
    for name,ref in refs:
        d=sum((a-b)**2 for a,b in zip(c,ref))
        if d<bd: bd,best=d,name
    return best

print(f"keep={keep}  ->  PDF pages={doc.page_count}  (期望 {len(keep)})")
for pno in range(doc.page_count):
    page = doc[pno]
    pix = page.get_pixmap(dpi=72)
    w, hh = pix.width, pix.height
    x = w // 2
    segs = []
    prev = None
    for y in range(hh):
        k = cls(pix.pixel(x, y)[:3])
        if k != prev:
            segs.append(f"{y/hh*1123:.0f}px:{k}")
            prev = k
    print(f"   P{pno+1}: " + " | ".join(segs))
