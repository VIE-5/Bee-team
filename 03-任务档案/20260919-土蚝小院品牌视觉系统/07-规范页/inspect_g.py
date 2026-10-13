# -*- coding: utf-8 -*-
"""规范页 1:1 局部核查裁片"""
import os
from PIL import Image
ROOT = r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉系统"
IM = os.path.join(ROOT, r"07-规范页\土蚝小院-品牌视觉规范-A4-3200x5760.png")
OUT = os.path.join(ROOT, r"07-规范页\_核查")
os.makedirs(OUT, exist_ok=True)
im = Image.open(IM).convert("RGB")
for n, b in [("g0-Logo卡与净空框", (180, 660, 1560, 1760)),
             ("gA-01右栏规则", (1500, 620, 3060, 1740)),
             ("gB-色卡第一行", (180, 1940, 1740, 2560)),
             ("gC-墨卡与用色规则", (1600, 2590, 3060, 3200)),
             ("gD-安全区行与铁律", (880, 4260, 3060, 5240)),
             ("gE-禁用清单", (180, 5300, 1740, 5640))]:
    im.crop(b).save(os.path.join(OUT, n + ".png"))
print("ok")
