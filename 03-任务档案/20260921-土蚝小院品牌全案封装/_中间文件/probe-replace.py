# -*- coding: utf-8 -*-
"""探测四张替换附件的尺寸 / 比例 / 有无边框留白。"""
from PIL import Image
import os

SRC = r'C:\Users\27612\.workbuddy\clipboard-images'
FILES = {
    'P05': 'clipboard-2026-09-21T10-09-11-146Z-fa7da6db.jpg',
    'P27': 'clipboard-2026-09-21T10-09-11-150Z-826f79d7.jpg',
    'P34': 'clipboard-2026-09-21T10-09-11-160Z-3d988465.jpg',
    'P29': 'clipboard-2026-09-21T10-09-11-163Z-996356c2.jpg',
}
for tag, fn in FILES.items():
    p = os.path.join(SRC, fn)
    with Image.open(p) as im:
        w, h = im.size
        print('%-4s %-52s %5dx%-5d  ratio=%.4f  %7.0f KB  mode=%s'
              % (tag, fn[-28:], w, h, w / h, os.path.getsize(p) / 1024, im.mode))
