# -*- coding: utf-8 -*-
"""1:1 局部放大核查：副标与 Logo 尾部是否打架、正文与砂锅间隙"""
import os
from PIL import Image
ROOT = r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉系统"
SRC = os.path.join(ROOT, r"06-成品\土蚝小院-抖音竖版主KV-1080x1920.png")
OUT = os.path.join(ROOT, r"06-成品\_核查")
os.makedirs(OUT, exist_ok=True)
im = Image.open(SRC)
crops = {
    "A-Logo与副标区_y390-600": (200, 390, 900, 600),
    "B-正文与砂锅间隙_y760-960": (300, 760, 1000, 960),
}
for k, box in crops.items():
    c = im.crop(box)
    c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
    p = os.path.join(OUT, k + ".png")
    c.save(p)
    print(k, box, "→", c.size)
