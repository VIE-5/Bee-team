import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(BASE, "fin", "png")
OUT = os.path.join(BASE, "out")
os.makedirs(OUT, exist_ok=True)

PAPER = (244, 241, 234)
INK = (35, 33, 31)
GREEN = (31, 78, 74)
BLUE = (36, 80, 90)
CRIM = (192, 57, 43)
GRAY = (120, 116, 108)

MARKS = [
    ("01-mei-seal", "梅 章", "传统徽章 · 墨绿 #1F4E4A", "徽"),
    ("02-fish-moon", "鱼 跃", "现代几何 · 石青 #24505A", "主"),
    ("03-seal-fish", "鱼 印", "印章负空间 · 玄墨 #23211F", "印"),
]


def tint(im, rgb):
    im = im.convert("RGBA")
    solid = Image.new("RGBA", im.size, rgb + (0,))
    solid.putalpha(im.getchannel("A"))
    return solid


def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()


CN_L = "C:/Windows/Fonts/msyhl.ttc"
CN = "C:/Windows/Fonts/msyh.ttc"
LAT = "C:/Windows/Fonts/segoeuil.ttf"

f_title = font(CN, 76)
f_sub = font(CN_L, 34)
f_name = font(CN, 40)
f_desc = font(CN_L, 26)
f_small = font(CN_L, 24)
f_tag = font(LAT, 26)
f_sw = font(LAT, 24)

# ---- 生成 单色 / 反白 ----
loaded = {}
for key, *_ in MARKS:
    im = Image.open(os.path.join(FIN, key + "_1024.png")).convert("RGBA")
    loaded[key] = im
    tint(im, (17, 17, 17)).save(os.path.join(OUT, key + "_mono.png"))
    rev = tint(im, (247, 242, 231))
    bg = Image.new("RGBA", im.size, (35, 33, 31, 255))
    bg.alpha_composite(rev)
    bg.convert("RGB").save(os.path.join(OUT, key + "_reverse.png"))

# ---- 展板 ----
W, H = 2160, 1640
board = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(board)

d.text((96, 88), "梅湖小院", font=f_title, fill=INK)
d.text((96, 190), "LOGO 提案  ·  矢量精绘版 V2   ｜   长沙 · 新中式庭院 · 人均 60", font=f_sub, fill=GRAY)
d.line([(96, 262), (W - 96, 262)], fill=(214, 208, 196), width=2)

# 三个方案卡
cw, ch, gap = 640, 520, 40
x0 = (W - (cw * 3 + gap * 2)) // 2
top = 320
for i, (key, name, desc, tag) in enumerate(MARKS):
    x = x0 + i * (cw + gap)
    d.rounded_rectangle([x, top, x + cw, top + ch], radius=22, fill=(255, 255, 255), outline=(226, 220, 208), width=2)
    m = loaded[key].resize((330, 330), Image.LANCZOS)
    board.paste(m, (x + (cw - 330) // 2, top + 46), m)
    d.text((x + cw // 2, top + 424), name, font=f_name, fill=INK, anchor="mm")
    d.text((x + cw // 2, top + 470), desc, font=f_desc, fill=GRAY, anchor="mm")
    d.rounded_rectangle([x + cw - 104, top + 20, x + cw - 24, top + 66], radius=14, fill=CRIM)
    d.text((x + cw - 64, top + 43), tag, font=f_small, fill=(255, 255, 255), anchor="mm")

# 应用性测试行
y2 = top + ch + 62
d.text((96, y2), "应用性测试", font=f_sub, fill=INK)
d.line([(300, y2 + 22), (W - 96, y2 + 22)], fill=(214, 208, 196), width=2)

by = y2 + 70
bh = 300
cols = [("小尺寸（缩到 32px 仍可辨）", "size"), ("单色黑（零渐变可用）", "mono"), ("反白（深底可用）", "reverse")]
bw = (W - 192 - 40 * 2) // 3
for i, (label, mode) in enumerate(cols):
    x = 96 + i * (bw + 40)
    d.rounded_rectangle([x, by, x + bw, by + bh], radius=18, fill=(255, 255, 255), outline=(226, 220, 208), width=2)
    d.text((x + 24, by + 22), label, font=f_small, fill=GRAY)
    cx = x + 26
    for j, (key, *_r) in enumerate(MARKS):
        if mode == "size":
            for k, s in enumerate([62, 40, 24]):
                m = loaded[key].resize((s, s), Image.LANCZOS)
                board.paste(m, (cx, by + 128 + (62 - s) // 2), m)
                cx += s + 12
            cx += 26
        elif mode == "mono":
            m = tint(loaded[key], (17, 17, 17)).resize((104, 104), Image.LANCZOS)
            board.paste(m, (cx, by + 130), m)
            cx += 116
        else:
            m = tint(loaded[key], (247, 242, 231)).resize((104, 104), Image.LANCZOS)
            tile = Image.new("RGBA", (104, 104), (35, 33, 31, 255))
            tile.alpha_composite(m)
            board.paste(tile.convert("RGB"), (cx, by + 130))
            cx += 116

# 色卡
y3 = by + bh + 56
d.text((96, y3), "色彩规范", font=f_sub, fill=INK)
d.line([(250, y3 + 22), (W - 96, y3 + 22)], fill=(214, 208, 196), width=2)
sw = [("墨绿", "#1F4E4A", GREEN), ("石青", "#24505A", BLUE), ("玄墨", "#23211F", INK),
      ("胭脂", "#C0392B", CRIM), ("宣纸米", "#F7F2E7", (247, 242, 231))]
sx = 96
for i, (nm, hexv, c) in enumerate(sw):
    x = sx + i * 300
    d.rounded_rectangle([x, y3 + 56, x + 250, y3 + 190], radius=14, fill=c, outline=(226, 220, 208))
    d.text((x, y3 + 206), nm, font=f_desc, fill=INK)
    d.text((x, y3 + 242), hexv, font=f_sw, fill=GRAY)

out = os.path.join(OUT, "梅湖小院-LOGO提案-展板V2.png")
board.save(out)
print("saved:", out, board.size)
