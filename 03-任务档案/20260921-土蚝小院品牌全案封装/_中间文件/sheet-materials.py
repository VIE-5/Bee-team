# -*- coding: utf-8 -*-
"""把独立物料 24 张拼成联系表，用于一次性识别内容分组。"""
import os
from PIL import Image, ImageDraw

D = r'E:\唐V-work\土蚝小院\土蚝\LOGO定\独立物料'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_materials-sheet.png')

fs = sorted(os.listdir(D))
COLS = 4
TH_W = 600
pad = 12
th_h = int(TH_W * 1086 / 1448)
rows = (len(fs) + COLS - 1) // COLS
W = COLS * (TH_W + pad) + pad
H = rows * (th_h + pad + 26) + pad

sheet = Image.new('RGB', (W, H), (245, 245, 245))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(fs):
    r, c = divmod(i, COLS)
    with Image.open(os.path.join(D, f)) as im:
        thumb = im.convert('RGB').resize((TH_W, th_h), Image.LANCZOS)
    x = pad + c * (TH_W + pad)
    y = pad + r * (th_h + pad + 26)
    sheet.paste(thumb, (x, y))
    core = f.replace('Codex 图像 2026年9月22日 ', '').replace('.png', '')
    d.text((x + 4, y + th_h + 5), '%02d  %s' % (i + 1, core), fill=(20, 20, 20))

sheet.save(OUT)
print('->', OUT, sheet.size, '%.0f KB' % (os.path.getsize(OUT) / 1024))
