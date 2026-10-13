# -*- coding: utf-8 -*-
"""土蚝小院 · 品牌视觉规范页（一页制 · A4 比例）
本机确定性渲染，不耗生成额度。色值/字体/几何全部取自 Brand Lock v2。
版式以逻辑单位 1600×2880 设计，S=2 超采样输出 3200×5760（A4@约 385dpi，可印）。
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉系统"
LOGO = os.path.join(ROOT, r"00-素材原始\Logo-土蚝小院-官方定版.png")
OUT = os.path.join(ROOT, "07-规范页")
os.makedirs(OUT, exist_ok=True)
FD = "C:/Windows/Fonts/"

# 色板（严格取自 Brand Lock v2）
SONG = (88, 104, 90)     # 58685A 岭南松柏绿
YANMI = (231, 220, 199)  # E7DCC7 暖米岩石色
HUTAO = (118, 86, 60)    # 76563C 深木胡桃色
DAI = (53, 70, 74)       # 35464A 黛青黑
ZHU = (163, 68, 53)      # A34435 朱砂红
TONG = (178, 138, 82)    # B28A52 铜金色
MO = (45, 48, 27)        # 2D301B 墨色（Logo 专用）
CARD = (240, 232, 216)   # 分区底＝基底提亮，仅版式用，非色板色
GREY = (110, 108, 96)    # 说明文字灰（墨色淡化）

S = 2
W, H = 1600 * S, 2880 * S
M = 100

def sc(v):
    return round(v * S)

def blend(c, base, a):
    return tuple(round(base[i] * (1 - a) + c[i] * a) for i in range(3))

def font(name, size, w=None):
    f = ImageFont.truetype(FD + name, max(1, sc(size)))
    if w is not None:
        try:
            f.set_variation_by_axes([w])
        except Exception:
            pass
    return f

SER = "NotoSerifSC-VF.ttf"; SAN = "NotoSansSC-VF.ttf"; MON = "consola.ttf"

def T(dr, x, y, s, f, fill, anchor="lm", tr=0):
    if tr == 0:
        dr.text((sc(x), sc(y)), s, font=f, fill=fill, anchor=anchor)
        return
    w = sum(f.getlength(c) for c in s) + sc(tr) * (len(s) - 1)
    cx = sc(x) - w / 2 if anchor[0] == "m" else sc(x)
    va = "l" + (anchor[1] if len(anchor) > 1 else "m")
    for c in s:
        dr.text((cx, sc(y)), c, font=f, fill=fill, anchor=va)
        cx += f.getlength(c) + sc(tr)

def tw(s, f, tr=0):
    return (sum(f.getlength(c) for c in s) + sc(tr) * (max(0, len(s) - 1))) / S

def Tfit(dr, x, y, s, name, size, weight, fill, maxw, anchor="lm", tr=0, floor=11):
    """按栏宽自动收字号，避免文字压边/出界（禁止靠截断字符串凑宽度）"""
    while size > floor:
        f = font(name, size, weight)
        if tw(s, f, tr) <= maxw:
            break
        size -= 1
    T(dr, x, y, s, f, fill, anchor, tr)
    return size

def RECT(dr, box, fill=None, outline=None, w=1):
    dr.rectangle([sc(box[0]), sc(box[1]), sc(box[2]), sc(box[3])], fill=fill,
                 outline=outline, width=sc(w))

def DASH(dr, box, color, w=1.5, dash=13, gap=9):
    x0, y0, x1, y1 = [sc(v) for v in box]
    dd, gg, ww = sc(dash), sc(gap), max(1, sc(w))
    x = x0
    while x < x1:
        dr.line([x, y0, min(x + dd, x1), y0], fill=color, width=ww)
        dr.line([x, y1, min(x + dd, x1), y1], fill=color, width=ww)
        x += dd + gg
    y = y0
    while y < y1:
        dr.line([x0, y, x0, min(y + dd, y1)], fill=color, width=ww)
        dr.line([x1, y, x1, min(y + dd, y1)], fill=color, width=ww)
        y += dd + gg

im = Image.new("RGB", (W, H), YANMI)
d = ImageDraw.Draw(im)

# ================= 页眉 =================
T(d, M, 112, "土蚝小院", font(SER, 84, 700), MO, "lm")
T(d, M + 356, 128, "BRAND VISUAL GUIDELINE", font(SAN, 20, 600), SONG, "lm", 5)
RECT(d, [M, 178, W - M, 181], ZHU)
T(d, M, 208, "品牌视觉规范 · v1.0 · 2026-09-19 · 岭南庭院院子餐厅 · 依据 Brand Lock v2（本页即生产合同）",
  font(SAN, 19, 400), GREY, "lm")

# ================= 01 Logo =================
T(d, M, 300, "01｜Logo 使用规范", font(SAN, 30, 900), MO, "lm")
RECT(d, [M, 348, M + 660, 848], CARD)
ink_x0, ink_y0, ink_w, ink_h = 449, 80, 785, 720
INK_W = 300
s = INK_W / ink_w
lg = Image.open(LOGO).convert("RGBA")
lg = lg.resize((round(lg.width * s * S), round(lg.height * s * S)), Image.LANCZOS)
# 墨迹中心置于卡中心 (M+330, 598)
icx, icy = M + 330, 598
lx = sc(icx - (ink_x0 * s + INK_W / 2)); ly = sc(icy - ink_h * s / 2)
box2 = (lx, ly, lx + lg.width, ly + lg.height)
im.paste(lg, (lx, ly), lg)
inkL, inkT = icx - INK_W / 2, icy - ink_h * s / 2
inkR, inkB = icx + INK_W / 2, icy + ink_h * s / 2
cs = ink_h * s * 0.25
DASH(d, [inkL - cs, inkT - cs, inkR + cs, inkB + cs], SONG, 1.5)
T(d, M + 24, 826, "虚线 ＝ 净空 Clear Space（墨迹高 ×25%）", font(SAN, 15, 400), GREY, "lm")

rules = [
    ("唯一官方文件", "Logo-土蚝小院-官方定版.png · 1671×941 · RGBA 透明底 · 只贴不改"),
    ("最小使用尺寸", "印刷 ≥ 30mm 宽 ｜ 数字 ≥ 120px 宽 ｜ 小于此值笔画会糊"),
    ("净空 Clear Space", "≥ 墨迹高度 25%（源尺寸约 180px）；底部可放宽至 200px 给落款呼吸"),
    ("允许变体", "深底反白稿 · 单色稿 —— 由官方文件「双色互换」算法生成，禁全白剪影"),
    ("禁止处理", "重绘 / 改字 / 加描边 / 投影 / 渐变 / 拆散重组 / 拉伸变形"),
    ("已知限制", "无矢量源：栅格可撑 A3（350×330mm@300dpi）；门头灯箱 / 丝印 / 烫金 需人工描摹矢量"),
]
y = 372
for t, s2 in rules:
    T(d, 820, y, t, font(SAN, 20, 700), MO, "lm")
    Tfit(d, 820, y + 30, s2, SAN, 17, 400, GREY, W - M - 820)
    y += 78

# ================= 02 色彩 =================
T(d, M, 930, "02｜色彩系统", font(SAN, 30, 900), MO, "lm")
sw = [
    (SONG, "岭南松柏绿", "#58685A", "品牌主色", "大色块 / 图形线；不作正文"),
    (YANMI, "暖米岩石色", "#E7DCC7", "基底 / 留白", "纸感底 / 文字承载带"),
    (HUTAO, "深木胡桃色", "#76563C", "器物 / 木料", "木器与辅助文字"),
    (DAI, "黛青黑", "#35464A", "深底 / 夜色", "深底物料 / 正文深色"),
    (ZHU, "朱砂红", "#A34435", "点睛色", "印章式点缀；面积 ≤5%"),
    (TONG, "铜金色", "#B28A52", "工艺色", "烫金 / 铜牌，不作平涂"),
    (MO, "墨色", "#2D301B", "Logo 专用", "仅 Logo 与墨色体系物料"),
]
cx0, cy0, cw, chh, gp = M, 980, 325, 292, 30
for i, (c, name, hx, role, use) in enumerate(sw):
    col = i % 4; row = i // 4
    x = cx0 + col * (cw + gp); yy = cy0 + row * (chh + gp)
    RECT(d, [x, yy, x + cw, yy + chh], CARD)
    RECT(d, [x, yy, x + cw, yy + 152], c)
    if c == YANMI:
        RECT(d, [x, yy + 150, x + cw, yy + 152], SONG)
    T(d, x + 20, yy + 186, name, font(SAN, 21, 700), MO, "lm")
    T(d, x + 20, yy + 220, hx, font(SAN, 18, 600), HUTAO if c != HUTAO else ZHU, "lm", 0.5)
    Tfit(d, x + 20, yy + 250, role, SAN, 16, 700, SONG, cw - 40)
    Tfit(d, x + 20, yy + 274, use, SAN, 14, 400, GREY, cw - 40)
# 第 8 格：用色规则
x = cx0 + 3 * (cw + gp); yy = cy0 + chh + gp
RECT(d, [x, yy, x + cw, yy + chh], CARD)
T(d, x + 20, yy + 34, "用色规则", font(SAN, 20, 700), MO, "lm")
for i, s2 in enumerate(["Logo 内印章红属标识内部色", "物料红一律 #A34435",
                        "点睛色面积 ≤5%", "深底正文 #E7DCC7 / 浅底 #35464A"]):
    Tfit(d, x + 20, yy + 74 + i * 32, "· " + s2, SAN, 14, 400, GREY, cw - 40)

# ================= 03 字体 =================
T(d, M, 1660, "03｜字体系统", font(SAN, 30, 900), MO, "lm")
fc = [("甲｜雅正宋", "思源宋体 Bold / 思源宋体", "商务宴请：菜单 · 名片 · 包厢物料",
       "岭南雅院 · 山野鲜宴", SER, 46, 700, SONG),
      ("丙｜招牌黑", "思源黑体 Heavy / 思源黑体", "抖音引流 · 促销 · 团购页",
       "来土蚝，吃生蚝，做土豪", SAN, 44, 900, MO)]
for i, (nm, spec, use, smp, ff, fs, fw, col) in enumerate(fc):
    x = M + i * 710
    RECT(d, [x, 1706, x + 680, 1950], CARD)
    RECT(d, [x, 1706, x + 6, 1950], col)
    T(d, x + 30, 1746, nm, font(SAN, 24, 900), MO, "lm")
    T(d, x + 30, 1780, spec, font(SAN, 16, 400), GREY, "lm")
    T(d, x + 30, 1850, smp, font(ff, fs, fw), col, "lm", 2)
    T(d, x + 30, 1912, use, font(SAN, 16, 700), SONG, "lm")
T(d, M, 1988, "授权均为 SIL OFL 免费商用 ｜ 中文一律确定性排版（PIL / HTML 渲染）—— 生成通道直出中文必出伪字",
  font(SAN, 17, 400), GREY, "lm")

# ================= 04 抖音竖版安全区 =================
T(d, M, 2060, "04｜抖音竖版安全区与构图铁律", font(SAN, 30, 900), MO, "lm")
dx, dy, dw, dh = 130, 2120, 259, 461
RECT(d, [dx, dy, dx + dw, dy + dh], blend(ZHU, YANMI, 0.20), MO, 1.5)
RECT(d, [dx, dy + round(130 * dh / 1920), dx + dw, dy + round(1440 * dh / 1920)], blend(SONG, YANMI, 0.16))
RECT(d, [dx, dy + round(1440 * dh / 1920), dx + dw, dy + dh], blend(ZHU, YANMI, 0.20))
DASH(d, [dx + round(64 * dw / 1080), dy, dx + round(1016 * dw / 1080), dy + dh], MO, 1, 8, 6)
T(d, dx + dw / 2, dy + 18, "遮挡", font(SAN, 13, 700), ZHU, "mm")
T(d, dx + dw / 2, dy + 200, "安全信息带", font(SAN, 15, 700), SONG, "mm")
T(d, dx + dw / 2, dy + 250, "y 130 – 1440", font(SAN, 13, 400), GREY, "mm")
T(d, dx + dw / 2, dy + 420, "遮挡", font(SAN, 13, 700), ZHU, "mm")
T(d, dx + dw / 2, dy + dh + 26, "1080 × 1920", font(SAN, 15, 700), MO, "mm")

T(d, 470, 2124, "抖音竖版 1080 × 1920 px ｜ 9:16 满屏", font(SAN, 26, 900), MO, "lm")
rows = [("顶部遮挡", "y 0 – 130", "不放任何信息"),
        ("安全信息带", "y 130 – 1440", "全部文字与 Logo 必须落在此区间"),
        ("底部遮挡", "y 1440 – 1920", "昵称 / 文案 / 音乐条 / 按钮；允许被裁切"),
        ("版　心", "左右各 64 px", "文字块不越 x 64 – 1016")]
for i, (a, b, c) in enumerate(rows):
    yy = 2180 + i * 52
    T(d, 470, yy, a, font(SAN, 19, 700), MO, "lm")
    Tfit(d, 640, yy, b, SAN, 18, 400, HUTAO, 150)
    Tfit(d, 800, yy, c, SAN, 18, 400, GREY, W - M - 800)
RC = [470, 2390, 1500, 2560]
RECT(d, RC, blend(ZHU, YANMI, 0.13))
RECT(d, [RC[0], RC[1], RC[0] + 6, RC[3]], ZHU)
T(d, 500, 2426, "构图铁律", font(SAN, 20, 900), ZHU, "lm")
T(d, 500, 2466, "不得用实色文字带横盖画面中下段 —— 会把产品（生蚝 / 砂锅）整段盖掉。",
  font(SAN, 17, 400), MO, "lm")
T(d, 500, 2498, "正确解法：文字落在画面自带的浅色留白（墙面）上；画面无留白时改为「上图下字」分区版式。",
  font(SAN, 17, 400), MO, "lm")
T(d, 500, 2534, "横竖版必须各自重新构图生成，禁止裁切另一画幅凑数。", font(SAN, 17, 400), MO, "lm")

# ================= 05 禁用 =================
T(d, M, 2650, "05｜禁用清单", font(SAN, 30, 900), MO, "lm")
RECT(d, [M, 2692, W - M, 2802], CARD)
RECT(d, [M, 2692, M + 6, 2802], ZHU)
ban_l = ["海浪 · 沙滩 · 渔网 · 海鸥 · 蓝海面", "生蚝拟人化 / 卡通 / 过度海鲜化"]
ban_r = ["画面内出现文字或 Logo（一律后期确定性合成）", "蓝调色偏 / 霓虹 / HDR 过锐 / 拉伸变形或改绘 Logo"]
for i in range(2):
    T(d, M + 30, 2722 + i * 34, "· " + ban_l[i], font(SAN, 17, 400), MO, "lm")
    T(d, 820, 2722 + i * 34, "· " + ban_r[i], font(SAN, 17, 400), MO, "lm")

# ================= 页脚 =================
RECT(d, [M, 2840, W - M, 2842], blend(MO, YANMI, 0.35))
T(d, M, 2862, "土蚝小院 · 品牌视觉规范 v1.0 · 2026-09-19 · 色值 / 字体 / Logo 规格与 Brand Lock v2 同步",
  font(SAN, 16, 400), GREY, "lm")
T(d, W - M, 2862, "生成通道只负责「无字画面」；中文与 Logo 一律确定性合成", font(SAN, 16, 400), GREY, "rm")

# 字体回退提示
out = os.path.join(OUT, "土蚝小院-品牌视觉规范-A4-3200x5760.png")
im.save(out)
print("saved", out, im.size)
