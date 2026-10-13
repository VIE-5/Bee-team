# -*- coding: utf-8 -*-
"""列出独立物料目录全部文件（含新增）。"""
import os
from PIL import Image

D = r'E:\唐V-work\土蚝小院\土蚝\LOGO定\独立物料'
fs = sorted(os.listdir(D))
print('count:', len(fs))
print('-' * 78)
for f in fs:
    p = os.path.join(D, f)
    with Image.open(p) as im:
        w, h = im.size
    print('%5dx%-5d %8.0f KB  %s' % (w, h, os.path.getsize(p) / 1024, f))
