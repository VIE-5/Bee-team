# -*- coding: utf-8 -*-
"""土蚝小院素材分析 · 第三轮：Logo 印章红的实色、蓝移像素排查、墨迹包围盒"""
from collections import Counter
from PIL import Image

LOGO = r"E:\唐V-work\土蚝小院\土蚝\LOGO定\task-mu6sp8rv3w83z.png"
im = Image.open(LOGO).convert("RGBA")
W, H = im.size
px = im.load()

O = []
def w(s=""):
    O.append(str(s))
def hx(c):
    return "#%02X%02X%02X" % c[:3]

# 墨迹包围盒（alpha > 40）
minx, miny, maxx, maxy = W, H, -1, -1
allpx = list(im.getdata())
for i, p in enumerate(allpx):
    if p[3] > 40:
        x, y = i % W, i // W
        minx = min(minx, x); maxx = max(maxx, x)
        miny = min(miny, y); maxy = max(maxy, y)
w("=" * 56)
w(f"[墨迹包围盒] x {minx}~{maxx} (宽 {maxx-minx+1})  y {miny}~{maxy} (高 {maxy-miny+1})")
w(f"  画布 {W}x{H}  左边距 {minx}  右边距 {W-1-maxx}  上边距 {miny}  下边距 {H-1-maxy}")
w(f"  墨迹宽高比 {(maxx-minx+1)/(maxy-miny+1):.3f}")

# 印章红：只取 alpha>240 的实心像素聚类
solid = [p for p in allpx if p[3] > 240]
reds = [p for p in solid if p[0] > 100 and p[0]-p[1] > 40 and p[0]-p[2] > 40]
w(f"[印章红] alpha>240 红色像素 {len(reds)}")
if reds:
    cnt = Counter(reds)
    for col, n in cnt.most_common(5):
        w(f"   {hx(col)}  {col[:3]}  {n} px")
    # 最饱和（红度最高）的 5%
    reds.sort(key=lambda c: c[0] - (c[1] + c[2]) / 2, reverse=True)
    top = reds[:max(1, len(reds)//20)]
    m = tuple(sum(c[i] for c in top) // len(top) for i in range(3))
    w(f"  >> 前 5% 饱和红均值 {hx(m)} {m}")

# 墨绿：alpha>240 且非红
grs = [p for p in solid if not (p[0] > 100 and p[0]-p[1] > 40 and p[0]-p[2] > 40)]
cnt = Counter(grs)
w(f"[墨绿实色] alpha>240 非红像素 {len(grs)}")
for col, n in cnt.most_common(5):
    w(f"   {hx(col)}  {col[:3]}  {n} px")

# 蓝移像素排查（水印/异常冷色）
blue = [p for p in solid if p[2] > p[0] + 30 and p[2] > 90]
w(f"[冷色排查] 蓝移显著像素 {len(blue)}  {'（有异常，需目视）' if blue else '（无）'}")
if blue:
    cntb = Counter(blue)
    for col, n in cntb.most_common(3):
        w(f"   {hx(col)} {col[:3]} {n} px")

with open(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉系统\01-素材分析\analyze_result3.txt",
          "w", encoding="utf-8") as f:
    f.write("\n".join(O))
print("OK")
