# -*- coding: utf-8 -*-
"""探针：PDF 内嵌图像的 DPI 与尺寸，判断 2x 是否必要。"""
import re
import sys
from pathlib import Path

p = Path(sys.argv[1])
data = p.read_bytes()

# 统计内嵌图像对象
imgs = re.findall(rb"/Subtype\s*/Image", data)
print(f"文件 {p.name}  {p.stat().st_size/1024/1024:.1f} MB")
print(f"内嵌图像对象数：{len(imgs)}")

# 采样若干图像的 /Width /Height
dims = re.findall(rb"/Width\s+(\d+)[^>]{0,200}?/Height\s+(\d+)", data, re.S)
if not dims:
    dims = re.findall(rb"/Height\s+(\d+)[^>]{0,200}?/Width\s+(\d+)", data, re.S)
seen = []
for a, b in dims[:400]:
    w, h = int(a), int(b)
    if w < 50 or h < 50:
        continue
    seen.append((w, h))
seen = sorted(set(seen), reverse=True)
print(f"图像尺寸样本（去重后 {len(seen)} 种，列前 15）：")
for w, h in seen[:15]:
    # 页面 1360px 宽 = 1020pt；若图铺满页宽，等效 DPI = w / (1360/96)
    dpi_full = w / (1360 / 96)
    print(f"   {w} x {h}   (若铺满 1360px 宽 → 等效 {dpi_full:.0f} dpi)")
