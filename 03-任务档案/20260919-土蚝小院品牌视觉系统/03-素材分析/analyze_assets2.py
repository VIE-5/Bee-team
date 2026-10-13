# -*- coding: utf-8 -*-
"""土蚝小院素材分析 · 第二轮：按 alpha 通道正确测 Logo 墨色，并验证色卡承载的色值"""
from collections import Counter
from PIL import Image

LOGO = r"E:\唐V-work\土蚝小院\土蚝\LOGO定\task-mu6sp8rv3w83z.png"
MB01 = r"C:\Users\27612\.workbuddy\clipboard-images\clipboard-2026-09-19T01-29-59-052Z-4e615174.jpg"
MB05 = r"C:\Users\27612\.workbuddy\clipboard-images\clipboard-2026-09-19T01-29-59-055Z-40e1e57e.jpg"
DECLARED = {
    "岭南松柏绿": (0x58, 0x68, 0x5A),
    "暖米岩石色": (0xE7, 0xDC, 0xC7),
    "深木胡桃色": (0x76, 0x56, 0x3C),
    "黛青黑":     (0x35, 0x46, 0x4A),
    "朱砂红":     (0xA3, 0x44, 0x35),
    "铜金色":     (0xB2, 0x8A, 0x52),
}

O = []
def w(s=""):
    O.append(str(s))

def hx(c):
    return "#%02X%02X%02X" % c[:3]

# ---------- 1. Logo 墨色 ----------
im = Image.open(LOGO).convert("RGBA")
px = list(im.getdata())
n_all = len(px)
opaque = [p for p in px if p[3] > 200]
semi = [p for p in px if 20 < p[3] <= 200]
w("=" * 56)
w(f"[LOGO] 尺寸 {im.size}  总像素 {n_all}")
w(f"  不透明像素(alpha>200) {len(opaque)} = {len(opaque)*100.0/n_all:.2f}%")
w(f"  半透明像素(抗锯齿边) {len(semi)} = {len(semi)*100.0/n_all:.2f}%")
cnt = Counter(opaque)
w("  -- alpha>200 的主色（前 8）--")
for col, n in cnt.most_common(8):
    w(f"     {hx(col)}  {col[:3]}  {n} px")
mean_ink = tuple(sum(c[i] for c in opaque) // len(opaque) for i in range(3))
w(f"  >> 墨色加权均值 {hx(mean_ink)} {mean_ink}")
reds = [p for p in opaque if p[0] > 110 and p[0] - p[1] > 45 and p[0] - p[2] > 45]
if reds:
    mr = tuple(sum(c[i] for c in reds) // len(reds) for i in range(3))
    w(f"  >> 印章红均值 {hx(mr)} {mr}  像素 {len(reds)} = {len(reds)*100.0/len(opaque):.2f}% of ink")
greens = [p for p in opaque if p[1] >= p[0] and p[1] > p[2]]
if greens:
    mg = tuple(sum(c[i] for c in greens) // len(greens) for i in range(3))
    w(f"  >> 墨绿均值  {hx(mg)} {mg}  像素 {len(greens)} = {len(greens)*100.0/len(opaque):.2f}% of ink")

# ---------- 2. 色卡承载验证 ----------
for name, path in (("MOODBOARD-01", MB01), ("MOODBOARD-05", MB05)):
    img = Image.open(path).convert("RGB")
    data = list(img.getdata())
    tot = len(data)
    w("=" * 56)
    w(f"[{name}] 尺寸 {img.size}")
    for label, t in DECLARED.items():
        hit = [p for p in data if abs(p[0]-t[0]) <= 14 and abs(p[1]-t[1]) <= 14 and abs(p[2]-t[2]) <= 14]
        if hit:
            m = tuple(sum(c[i] for c in hit) // len(hit) for i in range(3))
            w(f"    {label:8s} 目标 {hx(t)}  实测均值 {hx(m)}  命中 {len(hit)} px = {len(hit)*100.0/tot:.3f}%")
        else:
            w(f"    {label:8s} 目标 {hx(t)}  未命中")

with open(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉系统\01-素材分析\analyze_result2.txt",
          "w", encoding="utf-8") as f:
    f.write("\n".join(O))
print("OK")
