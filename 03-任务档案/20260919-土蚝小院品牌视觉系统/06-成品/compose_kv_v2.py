# -*- coding: utf-8 -*-
"""土蚝小院 · 抖音竖版主 KV 合成 v2
v1 问题：830–1440 的实色文字带把产品（生蚝盘/砂锅）整段盖掉 → 餐厅 KV 无菜，判废。
v2 改法：裁掉源图底部（连带水印）→ 画面铺到 1400 线；文字直接落在浅色墙面留白上，产品全程可见。
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉系统"
SRC = os.path.join(ROOT, r"05-锚点图\Photographic_brand_key_visual__2026-09-19T01-47-15.png")
LOGO = os.path.join(ROOT, r"00-素材原始\Logo-土蚝小院-官方定版.png")
OUTDIR = os.path.join(ROOT, "06-成品")
F = "C:/Windows/Fonts/"

YANMI = (231, 220, 199); SONG = (88, 104, 90); MO = (45, 48, 27)
CW, CH = 1080, 1920

# ---------- 1. 定位水印（松阈值，先把它在哪量出来）----------
src = Image.open(SRC).convert("RGB")
W, H = src.size
sp = src.load()

def wm_scan(pix, x0, x1, y0, y1, bright=150, neutral=25):
    b = [x1, y1, -1, -1]
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, bl = pix[x, y]
            if min(r, g, bl) > bright and (max(r, g, bl) - min(r, g, bl)) < neutral:
                b[0] = min(b[0], x); b[1] = min(b[1], y)
                b[2] = max(b[2], x); b[3] = max(b[3], y)
    return b if b[2] > 0 else None

print("源图", src.size, "右下象限水印:", wm_scan(sp, int(W*0.7), W, int(H*0.75), H))

# ---------- 2. 裁剪源图（切掉底部，连水印一起走）----------
CUT = 1330
img = src.crop((0, 0, W, CUT))
SCALE = CW / W
img = img.resize((CW, int(img.height * SCALE)), Image.LANCZOS)
BAND_TOP = img.height
print(f"裁剪后源图 {W}x{CUT} → 缩放 {img.size}  实色岩米带自 y={BAND_TOP}")

cv = Image.new("RGB", (CW, CH), YANMI)
cv.paste(img, (0, 0))
d = ImageDraw.Draw(cv, "RGBA")
d.rectangle([0, BAND_TOP, CW, CH], fill=(231, 220, 199, 255))

# ---------- 3. Logo（官方文件确定性叠加，墨迹宽 300 / 净空 25%）----------
ink_x0, ink_y0, ink_w, ink_h = 449, 80, 785, 720
ls = 280.0 / ink_w
lg = Image.open(LOGO).convert("RGBA")
lg = lg.resize((int(lg.width * ls), int(lg.height * ls)), Image.LANCZOS)
lx = int(540 - (ink_x0 * ls + 140)); ly = int(205 - ink_y0 * ls)
cv.paste(lg, (lx, ly), lg)
print(f"Logo 墨迹 x {int(lx+ink_x0*ls)}~{int(lx+ink_x0*ls+280)}  y {int(ly+ink_y0*ls)}~{int(ly+ink_y0*ls+ink_h*ls)}  净空框顶 y={int(ly+ink_y0*ls-ink_h*ls*0.25)}")

def font(path, size, w=None):
    f = ImageFont.truetype(F + path, size)
    if w is not None:
        try:
            f.set_variation_by_axes([w])
        except Exception:
            pass
    return f

# ---------- 4. 中文排版：落在墙面留白上，不压产品 ----------
d.text((CW // 2, 528), "岭 南 雅 院 · 山 野 鲜 宴",
       font=font("NotoSerifSC-VF.ttf", 32, 400), fill=SONG, anchor="mm")
tf = font("NotoSansSC-VF.ttf", 100, 900)
for i, line in enumerate(["来土蚝", "吃生蚝", "做土豪"]):
    d.text((CW // 2, 610 + i * 104), line, font=tf, fill=MO, anchor="mm")

out = os.path.join(OUTDIR, "土蚝小院-抖音竖版主KV-1080x1920.png")
cv.save(out)
print("saved:", out)

# ---------- 5. 产物核对：水印残留 + 产品可见度 ----------
ck = Image.open(out).convert("RGB"); cp = ck.load()
# 5a 水印残留（近中性亮像素）区域：右半 + 下半
res = wm_scan(cp, CW // 2, CW, CH // 2, CH)
print("成品水印残留扫描(松阈值):", res if res else "无")
# 5b 产品区是否还是照片（非纯色）—— 取 y 900-1400 的色差
box = ck.crop((0, 900, CW, 1400)).convert("RGB")
small = box.resize((60, 25))
cols = list(small.getdata())
uniq = len(set(cols))
print(f"产品带 y900–1400 色彩种类(60x25 采样) = {uniq}  {'照片可见 ✓' if uniq > 40 else '疑似被盖 ✗'}")
print("产物:", os.path.getsize(out) // 1024, "KB", ck.size)
