# -*- coding: utf-8 -*-
"""横版锚点图：严格水印定位 + 关键边界量测 + 存核查裁片
严格阈值：水印是近白中性字，min(channel)>205 且 range<18。
报告直接以 utf-8 写入文件，避免 PowerShell 管道乱码。
"""
import os
from PIL import Image

ROOT = r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉系统"
SRC = os.path.join(ROOT, r"05-锚点图\Photographic_brand_key_visual__2026-09-19T01-54-26.png")
OUT = os.path.join(ROOT, r"05-锚点图\_核查")
os.makedirs(OUT, exist_ok=True)

im = Image.open(SRC).convert("RGB")
W, H = im.size
px = im.load()
L = []

def lum(p):
    return (p[0] * 299 + p[1] * 587 + p[2] * 114) // 1000

# 1 严格水印 bbox（只在右下角找）
b = [W, H, -1, -1]
for y in range(int(H * 0.85), H):
    for x in range(int(W * 0.8), W):
        r, g, bl = px[x, y]
        if min(r, g, bl) > 205 and (max(r, g, bl) - min(r, g, bl)) < 18:
            b[0] = min(b[0], x); b[1] = min(b[1], y)
            b[2] = max(b[2], x); b[3] = max(b[3], y)
L.append("严格水印 bbox = %s   宽=%s 高=%s" % (b, b[2] - b[0] + 1 if b[2] > 0 else 0, b[3] - b[1] + 1 if b[3] > 0 else 0))

# 2 砂锅左边缘：扫 y=700 行，找从暗到亮的跃迁
row = 700
prev = None
edges = []
for x in range(0, 420):
    v = lum(px[x, row])
    if prev is not None and abs(v - prev) > 22:
        edges.append((x, prev, v))
    prev = v
L.append("y=%d 行 x0-420 亮度跃迁点(前12): %s" % (row, edges[:12]))

# 3 生蚝盘最右可见范围：y 520-900 内近中性亮像素(贝壳瓷白)的最大 x
mx = -1
for y in range(520, 900, 2):
    for x in range(W - 1, 900, -1):
        r, g, bl = px[x, y]
        if lum((r, g, bl)) > 150 and (max(r, g, bl) - min(r, g, bl)) < 40:
            mx = max(mx, x); break
L.append("右侧近中性亮像素(桌沿/贝壳)最大 x = %d" % mx)

# 4 右带暗区起点：从右往左找连续 60 列平均亮度<90 的起点
band_start = W
for x in range(W - 1, 1100, -1):
    s = 0; n = 0
    for y in range(0, H, 8):
        s += lum(px[x, y]); n += 1
    if s / n < 88:
        band_start = x
    else:
        break
L.append("右侧连续暗带起点 x = %d (右侧 %d px 为前景虚化)" % (band_start, W - band_start))

# 5 底边水印行：y 逐行统计近白像素数
L.append("底部逐行近白像素计数:")
for y in range(900, H, 8):
    c = sum(1 for x in range(0, W, 2) if min(px[x, y]) > 205 and (max(px[x, y]) - min(px[x, y])) < 18)
    L.append("   y=%d  count=%d" % (y, c))

# 6 存核查裁片
im.crop((0, 300, 380, 1024)).save(os.path.join(OUT, "A-左缘砂锅_0-380.png"))
im.crop((1150, 300, W, H)).save(os.path.join(OUT, "B-右缘与生蚝_1150-1536.png"))

report = "\n".join(L)
with open(os.path.join(ROOT, r"05-锚点图\probe_h_report.txt"), "w", encoding="utf-8") as f:
    f.write(report)
print("ok")
