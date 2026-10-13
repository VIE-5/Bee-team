# -*- coding: utf-8 -*-
"""拼联系表：37 页缩略图排成网格，用于全册通读找可疑页。"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

src = Path(sys.argv[1])
out = Path(sys.argv[2])
files = sorted(src.glob("slide-*.png"), key=lambda p: int(p.stem.split("-")[1]))
print(f"{len(files)} 页")

COLS = 5
TH_W = 380
pad = 10
th_h = int(TH_W * 850 / 1360)
rows = (len(files) + COLS - 1) // COLS
W = COLS * (TH_W + pad) + pad
H = rows * (th_h + pad + 22) + pad

sheet = Image.new("RGB", (W, H), (238, 238, 238))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    r, c = divmod(i, COLS)
    im = Image.open(f).convert("RGB").resize((TH_W, th_h), Image.LANCZOS)
    x = pad + c * (TH_W + pad)
    y = pad + r * (th_h + pad + 22)
    sheet.paste(im, (x, y))
    d.text((x + 3, y + th_h + 4), f"P{int(f.stem.split('-')[1]):02d}", fill=(40, 40, 40))

sheet.save(out)
print(f"-> {out}  {sheet.size[0]}x{sheet.size[1]}  {out.stat().st_size/1024:.0f}KB")
