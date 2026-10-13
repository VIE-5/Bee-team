# -*- coding: utf-8 -*-
"""BrandLock v2 色板 CMYK 参考值 + 补全白底对比度。"""
from pathlib import Path
OUT = Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉规范\_中间文件")

P = [
    ("松柏绿",   "品牌主色",  (0x58, 0x68, 0x5A)),
    ("暖米岩石色", "基底留白",  (0xE7, 0xDC, 0xC7)),
    ("朱砂红",   "点睛色",    (0xA3, 0x44, 0x35)),
    ("黛青黑",   "深底夜色",  (0x35, 0x46, 0x4A)),
    ("深木胡桃色", "器物木料",  (0x76, 0x56, 0x3C)),
    ("铜金色",   "工艺金",    (0xB2, 0x8A, 0x52)),
    ("标志墨色",  "标识内部色", (0x2D, 0x30, 0x1B)),
    ("印章红",   "标识内部色", (0xDE, 0x1C, 0x19)),
]

def cmyk(rgb):
    r, g, b = [v / 255.0 for v in rgb]
    k = 1 - max(r, g, b)
    if k >= 1: return (0, 0, 0, 100)
    return tuple(int(round(v * 100)) for v in
                 ((1-r-k)/(1-k), (1-g-k)/(1-k), (1-b-k)/(1-k), k))

def lin(c):
    c /= 255.0
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def lum(rgb):
    return 0.2126*lin(rgb[0]) + 0.7152*lin(rgb[1]) + 0.0722*lin(rgb[2])
def cr(a, b):
    la, lb = lum(a), lum(b); hi, lo = max(la, lb), min(la, lb)
    return (hi+0.05)/(lo+0.05)

rep = open(OUT / "cmyk-brandlock.report.txt", "w", encoding="utf-8")
def W(*a):
    s = " ".join(str(x) for x in a); print(s); rep.write(s+"\n")

W("=== BrandLock v2 色值表 / CMYK 参考（网式换算，非 ICC 分色）")
for nm, role, rgb in P:
    c, m, y, k = cmyk(rgb)
    W("  %-12s %-10s #%02X%02X%02X  rgb%-16s C%-3d M%-3d Y%-3d K%-3d"
      % (nm, role, rgb[0], rgb[1], rgb[2], str(rgb), c, m, y, k))
W("")
W("=== 纯白与岩石米底上的对比度补全")
INK  = (0x2D, 0x30, 0x1B)
RED  = (0xDE, 0x1C, 0x19)
ROCK = (0xE7, 0xDC, 0xC7)
WHITE= (0xFF, 0xFF, 0xFF)
CINN = (0xA3, 0x44, 0x35)
for gname, g in (("岩石米", ROCK), ("纯白", WHITE)):
    W("  %s : 正稿墨绿主体 %.2f:1 | 反白岩石米主体 %.2f:1 | 朱印红 %.2f:1 | 物料朱砂红 %.2f:1"
      % (gname, cr(INK, g), cr(ROCK, g), cr(RED, g), cr(CINN, g)))
W("")
W("=== 铜金在各底（决定烫金能用在哪）")
for gname, g in (("岩石米", ROCK), ("松柏绿", (0x58,0x68,0x5A)), ("黛青黑", (0x35,0x46,0x4A)), ("胡桃", (0x76,0x56,0x3C))):
    W("  铜金 on %-4s %.2f:1" % (gname, cr((0xB2,0x8A,0x52), g)))
rep.close()
