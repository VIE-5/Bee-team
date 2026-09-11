import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(BASE, "fin", "png")
FDIR = "C:/Users/27612/.workbuddy/binaries/node/workspace/_fonts/"
OUTDIR = os.path.join(BASE, "交付", "锁定版")
os.makedirs(OUTDIR, exist_ok=True)

CREAM = (247, 242, 231)
SERIF = FDIR + "NotoSerifSC-Light.otf"      # 思源宋体 Light / OFL
SANS = FDIR + "NotoSansSC-Light.otf"        # 思源黑体 Light / OFL
BRUSH = FDIR + "MaShanZheng-Regular.ttf"    # 马善政 / OFL

NAME = "梅湖小院"
LATIN = "MEIHU XIAOYUAN"

VERSIONS = [
    ("01-mei-seal", "01-梅章", "梅章", (31, 78, 74), SERIF, "思源宋体 Light"),
    ("02-fish-moon", "02-鱼跃", "鱼跃", (36, 80, 90), SANS, "思源黑体 Light"),
    ("03-seal-fish", "03-鱼印", "鱼印", (35, 33, 31), BRUSH, "马善政楷书"),
]


def tracked(d, x, y_center, text, font, fill, tracking=0, center_w=None):
    asc, desc = font.getmetrics()
    baseline = y_center + (asc - (asc + desc) / 2)
    widths = [d.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    cx = x if center_w is None else x + (center_w - total) / 2
    for c, w in zip(text, widths):
        d.text((cx, baseline), c, font=font, fill=fill, anchor="ls")
        cx += w + tracking
    return total


def h_lockup(mark_png, cn_font, ink, out):
    """横式锁定：图形在左，字标在右"""
    cn_size = 190
    MH = int(cn_size * 2.05)
    pad, gap = int(cn_size * 0.52), int(cn_size * 0.46)
    f_cn = ImageFont.truetype(cn_font, cn_size)
    lat_size = int(cn_size * 0.20)
    f_lat = ImageFont.truetype(SANS, lat_size)
    track_cn = int(cn_size * 0.05)
    track_lat = int(lat_size * 0.42)

    tmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    cn_w = sum(tmp.textlength(c, font=f_cn) for c in NAME) + track_cn * (len(NAME) - 1)
    lat_w = sum(tmp.textlength(c, font=f_lat) for c in LATIN) + track_lat * (len(LATIN) - 1)
    tw = max(cn_w, lat_w)

    W = int(pad + MH + gap + tw + pad)
    H = MH + pad * 2
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    mark = Image.open(mark_png).convert("RGBA").resize((MH, MH), Image.LANCZOS)
    im.paste(mark, (int(pad), int(pad)), mark)

    tx = pad + MH + gap
    tracked(d, tx, pad + MH * 0.40, NAME, f_cn, ink, track_cn)
    tracked(d, tx, pad + MH * 0.745, LATIN, f_lat, (140, 135, 125), track_lat)
    im.save(out)
    return im


def v_lockup(mark_png, cn_font, ink, out):
    """竖式锁定：图形在上，字标在下"""
    cn_size = 150
    MH = int(cn_size * 2.0)
    pad = int(cn_size * 0.55)
    gap = int(cn_size * 0.5)
    f_cn = ImageFont.truetype(cn_font, cn_size)
    lat_size = int(cn_size * 0.19)
    f_lat = ImageFont.truetype(SANS, lat_size)
    track_cn = int(cn_size * 0.10)
    track_lat = int(lat_size * 0.40)

    tmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    cn_w = sum(tmp.textlength(c, font=f_cn) for c in NAME) + track_cn * (len(NAME) - 1)
    lat_w = sum(tmp.textlength(c, font=f_lat) for c in LATIN) + track_lat * (len(LATIN) - 1)
    inner = max(MH, cn_w, lat_w)
    W = int(inner + pad * 2)
    H = int(pad + MH + gap + cn_size * 1.5 + pad)

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    mark = Image.open(mark_png).convert("RGBA").resize((MH, MH), Image.LANCZOS)
    im.paste(mark, (int((W - MH) / 2), int(pad)), mark)

    tracked(d, 0, pad + MH + gap + cn_size * 0.55, NAME, f_cn, ink, track_cn, center_w=W)
    tracked(d, 0, pad + MH + gap + cn_size * 1.15, LATIN, f_lat, (140, 135, 125), track_lat, center_w=W)
    im.save(out)
    return im


made = {}
for key, dirn, label, ink, cnf, fname in VERSIONS:
    mk = os.path.join(FIN, key + "_1024.png")
    h = h_lockup(mk, cnf, ink, os.path.join(OUTDIR, f"梅湖小院-LOGO-{label}-锁定-横式.png"))
    v = v_lockup(mk, cnf, ink, os.path.join(OUTDIR, f"梅湖小院-LOGO-{label}-锁定-竖式.png"))
    made[key] = (h, v, label, ink, fname)
    print(f"{label}: 横式 {h.size} / 竖式 {v.size}  字体={fname}")

# ---------- 规范板 ----------
f_title = ImageFont.truetype(SERIF, 86)
f_sub = ImageFont.truetype(SANS, 30)
f_sec = ImageFont.truetype(SANS, 40)
f_lab = ImageFont.truetype(SANS, 30)
f_note = ImageFont.truetype(SANS, 26)

BW = 2240
HDR, CARD_H, GAP = 300, 430, 34
V_H = 800
FW = 300
BH = HDR + 90 + 3 * (CARD_H + GAP) + 120 + V_H + 40 + FW

board = Image.new("RGB", (BW, BH), CREAM)
d = ImageDraw.Draw(board)
d.text((96, 84), "梅湖小院", font=f_title, fill=(35, 33, 31))
d.text((96, 196), "中文字标锁定版 · 图形标 + 品牌名组合规范   ｜   字体均为 SIL OFL 开源可商用", font=f_sub, fill=(140, 135, 125))
d.line([(96, 262), (BW - 96, 262)], fill=(214, 208, 196), width=2)

y = HDR + 40
d.text((96, y), "一 · 横式锁定（图形在左 / 字标在右）", font=f_sec, fill=(35, 33, 31))
y += 84
for key, dirn, label, ink, cnf, fname in VERSIONS:
    h = made[key][0]
    card_w = BW - 192
    d.rounded_rectangle([96, y, 96 + card_w, y + CARD_H], radius=20, fill=(255, 255, 255), outline=(226, 220, 208), width=2)
    scale = (CARD_H - 96) / h.height
    hh = h.resize((int(h.width * scale), int(h.height * scale)), Image.LANCZOS)
    board.paste(hh, (96 + (card_w - hh.width) // 2, y + 48), hh.split()[3])
    d.text((96 + card_w - 220, y + 32), f"{label} · {fname}", font=f_note, fill=(140, 135, 125))
    y += CARD_H + GAP

y += 60
d.text((96, y), "二 · 竖式锁定（图形在上 / 字标在下）", font=f_sec, fill=(35, 33, 31))
y += 96
for i, (key, dirn, label, ink, cnf, fname) in enumerate(VERSIONS):
    v = made[key][1]
    cw = (BW - 192 - 2 * GAP) // 3
    x = 96 + i * (cw + GAP)
    d.rounded_rectangle([x, y, x + cw, y + V_H], radius=20, fill=(255, 255, 255), outline=(226, 220, 208), width=2)
    s = (V_H - 130) / v.height
    vv = v.resize((int(v.width * s), int(v.height * s)), Image.LANCZOS)
    board.paste(vv, (x + (cw - vv.width) // 2, y + 34), vv.split()[3])
    d.text((x + cw // 2, y + V_H - 46), f"{label} · {fname}", font=f_note, fill=(140, 135, 125), anchor="mm")

y += V_H + 40
notes = [
    "字 体 ｜ 01 梅章→思源宋体 Light　02 鱼跃→思源黑体 Light　03 鱼印→马善政楷书　（全部 SIL OFL 1.1，免费商用）",
    "安 全 留 白 ｜ 字标四周预留 ≥ 图形高度 25% 的空间，不得被其他元素侵入",
    "最小使用尺寸 ｜ 横式整体高度 ≥ 40px；竖式整体高度 ≥ 56px",
    "禁 止 项 ｜ 不得拉伸变形 · 不得改色 · 不得加描边阴影 · 不得重排字距",
]
for i, t in enumerate(notes):
    d.text((96, y + i * 44), t, font=f_note, fill=(120, 116, 108))

out = os.path.join(BASE, "交付", "梅湖小院-中文字标锁定版-规范.png")
board.save(out)
print("saved:", out, board.size)
