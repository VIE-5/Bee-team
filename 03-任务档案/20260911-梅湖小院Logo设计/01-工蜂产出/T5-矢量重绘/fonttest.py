import os
from PIL import Image, ImageDraw, ImageFont

FONTS = "C:/Users/27612/.workbuddy/binaries/node/workspace/_fonts"
OUT = os.path.dirname(os.path.abspath(__file__))
cans = [
    ("NotoSansSC[wght].ttf", "思源黑体 Noto Sans SC", True),
    ("ZCOOLXiaoWei-Regular.ttf", "站酷小薇 ZCOOL XiaoWei", False),
    ("MaShanZheng-Regular.ttf", "马善政 Ma Shan Zheng", False),
]

im = Image.new("RGB", (1700, 3 * 260 + 40), (247, 242, 231))
d = ImageDraw.Draw(im)
y = 20
for fn, label, variable in cans:
    p = os.path.join(FONTS, fn)
    try:
        f = ImageFont.truetype(p, 130)
        vinfo = ""
        if variable:
            try:
                axes = f.get_variation_axes()
                vinfo = " axes=" + str([(a["name"], a["minimum"], a["maximum"]) for a in axes])
                f.set_variation_by_axes([300])
                vinfo += " -> set 300 OK"
            except Exception as e:
                vinfo = f" variation FAIL: {e}"
        d.text((30, y), f"{label}{vinfo}", font=ImageFont.truetype(p, 26), fill=(120, 116, 108))
        d.text((30, y + 46), "梅湖小院", font=f, fill=(31, 78, 74))
        d.text((760, y + 90), "MEIHU COURTYARD", font=ImageFont.truetype(FONTS + "/NotoSansSC[wght].ttf", 44), fill=(120, 116, 108))
    except Exception as e:
        d.text((30, y + 46), f"LOAD FAIL: {e}", font=ImageFont.load_default(), fill=(192, 57, 43))
    y += 260

im.save(os.path.join(OUT, "_font-test.png"))
print("saved _font-test.png", im.size)
