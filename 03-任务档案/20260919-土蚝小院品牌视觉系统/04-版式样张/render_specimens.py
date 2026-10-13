# -*- coding: utf-8 -*-
"""土蚝小院 · 阶段二样张渲染
产出 1：字体配对样张（3 组，用于主人选字体）
产出 2：抖音竖版版式骨架 1080×1920（安全区 + Logo 落位 + 文案排版）
注：Logo 一律从官方文件确定性合成，绝不重绘。
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉系统\04-版式样张"
os.makedirs(OUT, exist_ok=True)

F = "C:/Windows/Fonts/"
LOGO = r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉系统\00-素材原始\Logo-土蚝小院-官方定版.png"

# 品牌色（Brand Lock v2）
YANMI = (231, 220, 199)   # #E7DCC7 岩米
SONG  = (88, 104, 90)     # #58685A 松柏绿
DAI   = (53, 70, 74)      # #35464A 黛青黑
ZHU   = (163, 68, 53)     # #A34435 朱砂红
HU    = (118, 86, 60)     # #76563C 胡桃
MO    = (45, 48, 27)      # #2D301B Logo 墨色


def font(path, size, wght=None):
    f = ImageFont.truetype(F + path, size)
    if wght is not None:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f


# ============================================================
# 产出 1 · 字体配对样张
# ============================================================
W, H = 1600, 1290
im = Image.new("RGB", (W, H), YANMI)
d = ImageDraw.Draw(im)

SLOGAN = "来土蚝，吃生蚝，做土豪"
SUB = "岭南雅院 · 山野鲜宴   LINGNAN COURTYARD FEAST"

d.text((80, 56), "土蚝小院 · 广告语字体配对样张", font=font("NotoSansSC-VF.ttf", 40, 500), fill=DAI)
d.text((80, 112), "本机近似渲染：思源宋体 / 思源黑体 为真实候选；楷体为手写体近似替代（交付将换霞鹜文楷 OFL）",
       font=font("NotoSansSC-VF.ttf", 24, 400), fill=SONG)

ROWS = [
    ("甲｜雅正宋 · 思源宋体 Bold", "商务宴请 / 菜单 / 名片", "NotoSerifSC-VF.ttf", 700, "NotoSansSC-VF.ttf", 400),
    ("乙｜笔意楷 · 手写笔触（近似）", "家庭聚会 / 门店软装", "simkai.ttf", None, "NotoSerifSC-VF.ttf", 400),
    ("丙｜招牌黑 · 思源黑体 Heavy", "抖音引流 / 促销物料", "NotoSansSC-VF.ttf", 900, "NotoSansSC-VF.ttf", 400),
]

y = 200
for name, use, tfont, tw, bfont, bw in ROWS:
    d.line([(80, y), (W - 80, y)], fill=(200, 190, 172), width=1)
    d.text((80, y + 18), name, font=font("NotoSansSC-VF.ttf", 28, 500), fill=DAI)
    d.text((W - 80, y + 22), use, font=font("NotoSansSC-VF.ttf", 24, 400), fill=ZHU, anchor="ra")
    d.text((80, y + 62), SLOGAN, font=font(tfont, 88, tw), fill=MO)
    d.text((80, y + 186), SUB, font=font(bfont, 32, bw), fill=SONG)
    y += 360

d.text((80, H - 66), "选用规则：KV 主文案用标题字，副标/正文用正文。中文一律确定性排版，禁止生图直出。",
       font=font("NotoSansSC-VF.ttf", 24, 400), fill=HU)
im.save(os.path.join(OUT, "字体配对样张-3组.png"))
print("OK 1:", im.size)

# ============================================================
# 产出 2 · 抖音竖版版式骨架 1080×1920
# ============================================================
CW, CH = 1080, 1920
cv = Image.new("RGB", (CW, CH), YANMI)
d = ImageDraw.Draw(cv, "RGBA")

# 主视觉画面区（待生成，占位）
d.rectangle([0, 0, CW, 1920], fill=(220, 210, 190))
d.text((CW // 2, 700), "主视觉画面区", font=font("NotoSansSC-VF.ttf", 54, 500), fill=SONG, anchor="mm")
d.text((CW // 2, 758), "9:16 满幅 · 由生图通道产出（画面内无文字、无 Logo）",
       font=font("NotoSansSC-VF.ttf", 26, 400), fill=SONG, anchor="mm")

# 文字承载带（岩米，压住画面下段）
d.rectangle([0, 830, CW, 1440], fill=(231, 220, 199, 246))

# 副标
d.text((CW // 2, 892), "岭 南 雅 院 · 山 野 鲜 宴", font=font("NotoSerifSC-VF.ttf", 34, 400), fill=SONG, anchor="mm")

# 主文案三行三字
tf = font("NotoSansSC-VF.ttf", 118, 900)
for i, line in enumerate(["来土蚝", "吃生蚝", "做土豪"]):
    d.text((CW // 2, 1000 + i * 140), line, font=tf, fill=MO, anchor="mm")

# 朱砂印章式落款（辅助图形：小方印）
d.rectangle([870, 1330, 934, 1394], fill=ZHU)
d.text((902, 1362), "鲜", font=font("NotoSerifSC-VF.ttf", 40, 600), fill=YANMI, anchor="mm")

# ---- Logo 确定性合成（按墨迹包围盒落位）----
lg = Image.open(LOGO).convert("RGBA")
ink_w, ink_x0, ink_y0, ink_h = 785, 449, 80, 720
scale = 300.0 / ink_w
lg2 = lg.resize((int(lg.width * scale), int(lg.height * scale)), Image.LANCZOS)
px = int(540 - (ink_x0 * scale + 150))
py = int(230 - ink_y0 * scale)
cv.paste(lg2, (px, py), lg2)
# 净空框（源尺寸 25% 墨迹高 → 缩放后）
clr = int(ink_h * scale * 0.25)
d.rectangle([px + ink_x0 * scale - clr, py + ink_y0 * scale - clr,
             px + ink_x0 * scale + 300 + clr, py + ink_y0 * scale + ink_h * scale + clr],
            outline=ZHU, width=2)
d.text((px + ink_x0 * scale - clr, py + ink_y0 * scale + ink_h * scale + clr + 12),
       "Logo 净空 ≥25% 墨迹高", font=font("NotoSansSC-VF.ttf", 22, 400), fill=ZHU)

# ---- 安全区标注 ----
d.rectangle([0, 0, CW, 130], fill=(163, 68, 53, 40), outline=ZHU, width=2)
d.text((CW // 2, 65), "顶部遮挡区 0–130px（抖音 UI）· 不放信息",
       font=font("NotoSansSC-VF.ttf", 24, 400), fill=ZHU, anchor="mm")
d.rectangle([0, 1440, CW, 1919], fill=(163, 68, 53, 40), outline=ZHU, width=2)
d.text((CW // 2, 1520), "底部遮挡区 1440–1920px（昵称/文案/音乐条）",
       font=font("NotoSansSC-VF.ttf", 24, 400), fill=ZHU, anchor="mm")
d.text((CW // 2, 1556), "· 不放任何信息，允许被裁切",
       font=font("NotoSansSC-VF.ttf", 24, 400), fill=ZHU, anchor="mm")
# 版心线
d.line([(64, 130), (64, 1440)], fill=SONG, width=1)
d.line([(CW - 64, 130), (CW - 64, 1440)], fill=SONG, width=1)
d.text((72, 1748), "版心 左右各 64px ｜ 画布 1080×1920 ｜ 信息全部落在 130–1440 安全带内",
       font=font("NotoSansSC-VF.ttf", 24, 400), fill=ZHU)
cv.save(os.path.join(OUT, "抖音竖版-版式骨架-1080x1920.png"))
print("OK 2:", cv.size)
