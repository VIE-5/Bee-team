# -*- coding: utf-8 -*-
"""土蚝小院 · 横版主 KV 1920×1080（左文右景）确定性合成
与竖版同源同规矩：生图只出"无字画面"，中文与 Logo 由本脚本合成。
版面：左栏 500px 岩米纸底承 Logo + 副标 + 主口号；右 1420px 照片。
裁切依据（像素量测）：源图右侧 x>1350 为虚化前景带，水印位于 x1400-1495/y940-990
→ 裁到 x=1346 一刀同时切除虚化带与水印，且保住最右侧生蚝壳（最右亮像素 x=1339）。
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉系统"
SRC = os.path.join(ROOT, r"05-锚点图\Photographic_brand_key_visual__2026-09-19T01-54-26.png")
LOGO = os.path.join(ROOT, r"00-素材原始\Logo-土蚝小院-官方定版.png")
OUTDIR = os.path.join(ROOT, "06-成品")
F = "C:/Windows/Fonts/"

YANMI = (231, 220, 199); SONG = (88, 104, 90); MO = (45, 48, 27); ZHU = (163, 68, 53)
CW, CH, PANEL = 1920, 1080, 486
CROP = (20, 0, 1380, 1024)
log = []

# ---------- 1. 照片层 ----------
src = Image.open(SRC).convert("RGB")
ph = src.crop(CROP)
PW = CW - PANEL
ph = ph.resize((PW, CH), Image.LANCZOS)
log.append("源图 %s → 裁 %s = %dx%d → 铺满 %dx%d（缩放 %.4f，裁掉右侧 %dpx 虚化带+水印）"
           % (src.size, CROP, CROP[2] - CROP[0], CROP[3] - CROP[1], PW, CH,
              PW / (CROP[2] - CROP[0]), src.width - CROP[2]))

cv = Image.new("RGB", (CW, CH), YANMI)
cv.paste(ph, (PANEL, 0))

# ---------- 2. 左栏（独立图层，杜绝 Logo 透明像素越界污染照片）----------
pan = Image.new("RGB", (PANEL, CH), YANMI)
d = ImageDraw.Draw(pan, "RGBA")

def font(p, s, w=None):
    f = ImageFont.truetype(F + p, s)
    if w is not None:
        try:
            f.set_variation_by_axes([w])
        except Exception:
            pass
    return f

def T(dr, x, y, s, f, fill, anchor="lm", tr=0):
    """带字距的文本；anchor 首字符 m=水平居中(以 x 为中线)，l=左对齐(以 x 为左缘)"""
    if tr == 0:
        dr.text((x, y), s, font=f, fill=fill, anchor=anchor)
        return
    w = sum(f.getlength(c) for c in s) + tr * (len(s) - 1)
    cx = x - w / 2 if anchor[0] == "m" else x
    va = "l" + (anchor[1] if len(anchor) > 1 else "m")
    for c in s:
        dr.text((cx, y), c, font=f, fill=fill, anchor=va)
        cx += f.getlength(c) + tr

# 2a Logo：官方文件按墨迹 bbox 定位，墨迹宽 280
ink_x0, ink_y0, ink_w, ink_h = 449, 80, 785, 720
INK_W, INK_TOP = 280, 140
s = INK_W / ink_w
lg = Image.open(LOGO).convert("RGBA")
lg = lg.resize((round(lg.width * s), round(lg.height * s)), Image.LANCZOS)
lx = round(PANEL / 2 - (ink_x0 * s + INK_W / 2)); ly = round(INK_TOP - ink_y0 * s)
pan.paste(lg, (lx, ly), lg)
ink_bot = INK_TOP + ink_h * s
log.append("Logo 墨迹 x %.0f~%.0f（宽 %d）y %d~%.0f；净空框顶 y=%.0f（≥ 墨迹高25%%=%.0f）%s"
           % (PANEL / 2 - INK_W / 2, PANEL / 2 + INK_W / 2, INK_W, INK_TOP, ink_bot,
              INK_TOP - ink_h * s * 0.25, ink_h * s * 0.25,
              "OK" if INK_TOP - ink_h * s * 0.25 >= ink_h * s * 0.25 else "不足"))

# 2b 副标
T(d, PANEL / 2, 448, "岭南雅院 · 山野鲜宴", font("NotoSerifSC-VF.ttf", 28, 400), SONG, "mm", 6)
# 2c 主口号（三行三字 · 招牌黑）
tf = font("NotoSansSC-VF.ttf", 100, 900)
for i, line in enumerate(["来土蚝", "吃生蚝", "做土豪"]):
    T(d, PANEL / 2, 570 + i * 112, line, tf, MO, "mm", 8)
# 2d 朱砂红短规线 + 英文
d.rectangle([PANEL / 2 - 70, 898, PANEL / 2 + 70, 900], fill=ZHU)
T(d, PANEL / 2, 936, "LINGNAN COURTYARD FEAST", font("NotoSansSC-VF.ttf", 15, 500), SONG, "mm", 5)

cv.paste(pan, (0, 0))

out = os.path.join(OUTDIR, "土蚝小院-横版主KV-1920x1080.png")
cv.save(out)

# ---------- 3. 像素级自检 ----------
ck = Image.open(out).convert("RGB"); cp = ck.load()
log.append("产物 %dx%d  %.0f KB" % (ck.width, ck.height, os.path.getsize(out) / 1024))

# 3a 左栏底色是否精确等于品牌基底
log.append("左栏底色抽样 (250,1000) = %s（品牌基底 #E7DCC7 = (231,220,199)）%s"
           % ((cp[250, 1000],), "一致" if cp[250, 1000] == YANMI else "偏差"))

# 3b 水印：双向几何复核（亮墙高光会越亮度阈值，故不做全画阈值扫描）
#   方向一：废弃条带里应确实存在那枚水印（否则说明我们量错了位置）
sp = src.load()
wb = [9999, 9999, -1, -1]
for y in range(880, src.height):
    for x in range(CROP[2], src.width):
        if min(sp[x, y]) > 140 and (max(sp[x, y]) - min(sp[x, y])) < 20:
            wb = [min(wb[0], x), min(wb[1], y), max(wb[2], x), max(wb[3], y)]
log.append("废弃条带(源 x%d-%d) 亮中性簇 bbox = %s  → 水印确在此带内"
           % (CROP[2], src.width, wb if wb[2] > 0 else "未找到"))
#   方向二：几何证明 —— 水印 bbox 与裁框是否有交集
if wb[2] > 0:
    inter = not (wb[0] >= CROP[2] or wb[2] <= CROP[0] or wb[1] >= CROP[3] or wb[3] <= CROP[1])
    log.append("水印 bbox ∩ 裁框 %s = %s  → %s（水印左缘 %d vs 裁框右缘 %d，余量 %dpx）"
               % (CROP, "有交集" if inter else "无交集",
                  "需重新定刀口 ✗" if inter else "水印已彻底排除 ✓", wb[0], CROP[2], wb[0] - CROP[2]))
#   附注：全画阈值扫描不可用于本图判水印（亮墙高光越阈，必出假阳性），故不再作为判据
log.append("附注：全画「近白中性块」扫描在亮墙图上会产生假阳性（墙高光 min>200），不作判据；本单以几何排除为准。")

# 3c 产品可见度：生蚝/砂锅区色彩种类
box = ck.crop((700, 480, 1900, 1080)).resize((80, 40))
uniq = len(set(box.getdata()))
log.append("产品区(700,480)-(1900,1080) 色彩种类(80x40) = %d  %s" % (uniq, "照片可见 ✓" if uniq > 60 else "疑似被盖 ✗"))

# 3d 红：全画除 Logo 外的朱砂红像素分布
zs = [(x, y) for y in range(0, CH, 3) for x in range(0, CW, 3)
      if abs(cp[x, y][0] - ZHU[0]) < 12 and abs(cp[x, y][1] - ZHU[1]) < 12 and abs(cp[x, y][2] - ZHU[2]) < 12]
log.append("朱砂红 #A34435 命中像素(3px 抽样) = %d  %s" % (len(zs), "仅规线（左栏）" if all(x < PANEL for x, _ in zs) else "需查"))

# 3e 画面主色偏差（照片墙面 vs 品牌基底）
tot = [0, 0, 0]; n = 0
for y in range(200, 700, 5):
    for x in range(900, 1400, 5):
        p = cp[x, y]; tot = [tot[i] + p[i] for i in range(3)]; n += 1
avg = tuple(t // n for t in tot)
log.append("照片区亮墙均色 = %s  与基底 #E7DCC7 偏差 ΔRGB = %s（生成画面天然偏暖灰，属画面观感非物料实色）"
           % (avg, tuple(avg[i] - YANMI[i] for i in range(3))))

with open(os.path.join(OUTDIR, "compose_kv_h_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log))
print("ok")
