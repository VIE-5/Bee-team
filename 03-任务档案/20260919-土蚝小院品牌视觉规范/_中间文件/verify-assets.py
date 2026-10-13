# -*- coding: utf-8 -*-
"""
verify-assets.py —— 四版标志资产合成到「各自真实底色」的目视验证。

为什么必须做：反白稿是历史上最容易出事的一环 ——
曾出现「把可见像素全涂白 = 一坨无结构白块」，深底上直接废掉。
所以每轮资产重生成后，都要把四版合成到深底**用眼睛确认结构可辨**。

v2（2026-09-19）：底色改为 BrandLock v2 口径，8 格正好覆盖规范册 P11 矩阵的关键判定行。
"""
from pathlib import Path
from PIL import Image, ImageDraw

A = Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉规范\01-工蜂产出\assets")
OUTD = Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉规范\_中间文件")

ROCK     = (0xE7, 0xDC, 0xC7)   # 暖米岩石色（基底）
WHITE    = (0xFF, 0xFF, 0xFF)
PINE     = (0x58, 0x68, 0x5A)   # 松柏绿（品牌主色）
DARKBLUE = (0x35, 0x46, 0x4A)   # 黛青黑（深底夜色）
WALNUT   = (0x76, 0x56, 0x3C)   # 深木胡桃色

cases = [
    ("logo-primary.png",    ROCK,     "1 primary on ROCK  9.97 / 3.61  OK"),
    ("logo-primary.png",    WHITE,    "2 primary on WHITE 13.55 / 4.90 OK"),
    ("logo-primary.png",    PINE,     "3 primary on PINE  2.29 / 1.21  NO"),
    ("logo-primary.png",    WALNUT,   "4 primary on WALNUT 2.04 / 1.35 NO"),
    ("logo-reverse.png",    DARKBLUE, "5 reverse on DARK  7.27 / 2.02  *"),
    ("logo-reverse.png",    PINE,     "6 reverse on PINE  4.36 / 1.21  *"),
    ("logo-mono-cream.png", DARKBLUE, "7 mono-cream DARK  深底首选"),
    ("logo-mono-cream.png", PINE,     "8 mono-cream PINE  4.36 OK"),
]

CW, CH = 420, 420
cols = 4
rows = (len(cases) + cols - 1) // cols
sheet = Image.new("RGB", (cols * CW, rows * CH + rows * 26), (128, 128, 128))
d = ImageDraw.Draw(sheet)
for i, (fn, bg, label) in enumerate(cases):
    im = Image.open(A / fn).convert("RGBA")
    plate = Image.new("RGBA", (CW, CH - 26), bg + (255,))
    sc = min((CW - 40) / im.width, (CH - 26 - 40) / im.height)
    rs = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    plate.alpha_composite(rs, ((CW - rs.width) // 2, (CH - 26 - rs.height) // 2))
    r, c = divmod(i, cols)
    x, y = c * CW, r * CH
    sheet.paste(plate.convert("RGB"), (x, y))
    d.text((x + 8, y + CH - 20), label, fill=(20, 20, 20))
out = OUTD / "_asset-verify.png"
sheet.save(out, "PNG")
print("written", out, sheet.size)
