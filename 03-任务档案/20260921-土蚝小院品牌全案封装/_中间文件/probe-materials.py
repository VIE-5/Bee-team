# -*- coding: utf-8 -*-
"""探测独立物料目录：文件尺寸 + 从文件名批次推断分组。"""
import os
from PIL import Image

D = r'E:\唐V-work\土蚝小院\土蚝\LOGO定\独立物料'
fs = sorted(os.listdir(D))
print('总文件数:', len(fs))
print('-' * 74)
for f in fs:
    p = os.path.join(D, f)
    with Image.open(p) as im:
        w, h = im.size
    core = f.replace('Codex 图像 ', '').replace('.png', '')
    print('%-30s %5dx%-5d ratio=%.4f  %6.0f KB' % (core, w, h, w / h, os.path.getsize(p) / 1024))
