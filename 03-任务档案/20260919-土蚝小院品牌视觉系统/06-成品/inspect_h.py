# -*- coding: utf-8 -*-
"""横版成品 1:1 局部核查裁片（缩放预览会骗人，判几何必须 1:1）"""
import os
from PIL import Image

ROOT = r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉系统"
SRC = os.path.join(ROOT, r"05-锚点图\Photographic_brand_key_visual__2026-09-19T01-54-26.png")
FIN = os.path.join(ROOT, r"06-成品\土蚝小院-横版主KV-1920x1080.png")
OUT = os.path.join(ROOT, r"06-成品\_核查")
os.makedirs(OUT, exist_ok=True)

im = Image.open(FIN).convert("RGB")
im.crop((1540, 840, 1920, 1080)).save(os.path.join(OUT, "A-成品右下角1比1.png"))
im.crop((0, 60, 540, 520)).save(os.path.join(OUT, "B-左栏Logo区1比1.png"))
im.crop((0, 400, 540, 1030)).save(os.path.join(OUT, "C-左栏文字区1比1.png"))
im.crop((480, 0, 1100, 620)).save(os.path.join(OUT, "D-面板与照片接缝1比1.png"))
im.crop((1640, 360, 1920, 900)).save(os.path.join(OUT, "F-成品右缘产品1比1.png"))
Image.open(SRC).convert("RGB").crop((1330, 900, 1536, 1024)).save(os.path.join(OUT, "E-源废弃条带含水印1比1.png"))
with open(os.path.join(OUT, "list.txt"), "w", encoding="utf-8") as f:
    for n in sorted(os.listdir(OUT)):
        f.write("%s  %.0fKB\n" % (n, os.path.getsize(os.path.join(OUT, n)) / 1024))
print("ok")
