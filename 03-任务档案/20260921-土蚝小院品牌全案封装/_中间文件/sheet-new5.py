# -*- coding: utf-8 -*-
"""新增 5 张（09_53 批次）联系表。"""
import os
from PIL import Image, ImageDraw

D = r'E:\唐V-work\土蚝小院\土蚝\LOGO定\独立物料'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_new5-sheet.png')

fs = sorted(f for f in os.listdir(D) if '09_53' in f)
print('新增:', len(fs))

COLS = 3
TH_W = 760
pad = 14
th_h = int(TH_W * 1086 / 1448)
rows = (len(fs) + COLS - 1) // COLS
W = COLS * (TH_W + pad) + pad
H = rows * (th_h + pad + 28) + pad

sheet = Image.new('RGB', (W, H), (245, 245, 245))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(fs):
    r, c = divmod(i, COLS)
    with Image.open(os.path.join(D, f)) as im:
        thumb = im.convert('RGB').resize((TH_W, th_h), Image.LANCZOS)
    x = pad + c * (TH_W + pad)
    y = pad + r * (th_h + pad + 28)
    sheet.paste(thumb, (x, y))
    d.text((x + 4, y + th_h + 6), f.replace('Codex 图像 2026年9月22日 ', '').replace('.png', ''),
           fill=(20, 20, 20))

sheet.save(OUT)
print('->', OUT, sheet.size)
