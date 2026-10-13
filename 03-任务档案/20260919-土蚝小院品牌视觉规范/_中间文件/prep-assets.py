# -*- coding: utf-8 -*-
"""
prep-assets.py — 土蚝小院品牌视觉规范 · 标志资产加工 + 色值核算

源：定稿透明底 PNG（1671x941，实测标志外框 449,80 - 1233,799 = 785x720）

产出四版资产（均保留原透明底）：
  logo-primary.png    正稿      Logo 墨色 + 印章红（原色，不动）
  logo-reverse.png    反白版    墨色→暖米岩石色，印章红保留（深底用）
  logo-mono-green.png 单色墨    全色归一到 Logo 墨色，印章白字挖空
  logo-mono-cream.png 单色米白  全色归一到暖米岩石色，印章白字挖空（深底用）
  logo-seal.png       印章单体  供「认证/点睛」位使用

重着色用「三参考色逆距离软权重」，不用硬分类 —— 硬分类会在
印章红底与白字的抗锯齿过渡带上切出细白晕或细墨晕（2026-09-19 试过）。

────────────────────────────────────────────────────────────
v2 变更（2026-09-19，色表对齐 BrandLock v2）
  1. 反白版 / 单色米白版主体色 → 暖米岩石色 #E7DCC7（品牌基底色）。
     旧版用「宣纸米白 #FDF4E3」，那是从主人提供的**参考反白稿 JPG** 实测来的，
     而该 JPG 已明确「有损、只作参考、不作为色值依据」（见 00-任务图.md 第二节）。
     改用 BrandLock 基底色后，资产与规范册 P11 对比度矩阵的口径（反白主体＝岩石米）一致。
  2. 单色墨版主体 → Logo 墨色 #2D301B（BrandLock §3 明确允许「墨色体系」物料）。
  3. 印章红统一取定版值 #DE1C19（原实测众数 #DF1D1A，差 1/255 属量化噪声）。
  4. 最细笔画：改为**双向游程 + alpha>200**（剔除抗锯齿过渡带与孤立噪声点），
     输出 p1/p2/p5/p10/p25 全档，避免只用单一分位数造成规范值偏乐观。
"""
import json
from pathlib import Path
from PIL import Image

SRC = Path(r"E:\唐V-work\土蚝小院\土蚝\LOGO定\task-mu6sp8rv3w83z.png")
ROOT = Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉规范")
OUT = ROOT / "01-工蜂产出" / "assets"
OUT.mkdir(parents=True, exist_ok=True)
LOG = ROOT / "_中间文件"
LOG.mkdir(parents=True, exist_ok=True)
rep = open(LOG / "prep.report.txt", "w", encoding="utf-8")
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s); rep.write(s + "\n")

# ---- 色值（BrandLock v2 口径）----
INK        = (0x2D, 0x30, 0x1B)   # Logo 墨色（标识内部色；"墨色体系"物料可用）
SEAL_RED   = (0xDE, 0x1C, 0x19)   # 印章红（定版值 · 标识内部色）
SEAL_WHITE = (0xFF, 0xFF, 0xFF)   # 印章白字（阴刻留白）
ROCK       = (0xE7, 0xDC, 0xC7)   # 暖米岩石色 · 品牌基底（反白/单色米白 主体）
PINE       = (0x58, 0x68, 0x5A)   # 岭南松柏绿 · 品牌主色
CINNABAR   = (0xA3, 0x44, 0x35)   # 朱砂红 · 物料统一红（点睛，≤5%）
DARKBLUE   = (0x35, 0x46, 0x4A)   # 黛青黑 · 深底夜色
WALNUT     = (0x76, 0x56, 0x3C)   # 深木胡桃色 · 器物木料
BRONZE     = (0xB2, 0x8A, 0x52)   # 铜金色 · 工艺金


def to_cmyk(rgb):
    r, g, b = [v / 255.0 for v in rgb]
    k = 1 - max(r, g, b)
    if k >= 1:
        return (0, 0, 0, 100)
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return tuple(int(round(v * 100)) for v in (c, m, y, k))


def recolor(im, ink_target, white_mode):
    """ink_target: 墨色像素去向；white_mode: 'keep' 保留白字 | 'hole' 白字挖空"""
    px = im.load()
    W, H = im.size
    refs = [INK, SEAL_RED, SEAL_WHITE]
    tgt = [ink_target, SEAL_RED, None if white_mode == "hole" else SEAL_WHITE]
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            w = []
            for (rr, gg, bb) in refs:
                d2 = (r - rr) ** 2 + (g - gg) ** 2 + (b - bb) ** 2
                w.append(1.0 / (d2 + 64.0))
            s = sum(w)
            w = [v / s for v in w]
            nr = ng = nb = 0.0
            na = 0.0
            for wi, ti in zip(w, tgt):
                if ti is None:
                    continue
                nr += wi * ti[0]; ng += wi * ti[1]; nb += wi * ti[2]; na += wi
            if na <= 0:
                px[x, y] = (0, 0, 0, 0)
            else:
                px[x, y] = (int(round(nr / na)), int(round(ng / na)),
                            int(round(nb / na)), int(round(a * na)))
    return im


src = Image.open(SRC).convert("RGBA")
X0, Y0, X1, Y1 = 449, 80, 1233, 799        # 实测 alpha 外框
mark = src.crop((X0, Y0, X1 + 1, Y1 + 1))
P("mark crop : %dx%d  ratio %.4f" % (mark.width, mark.height,
                                     mark.width / float(mark.height)))

mark.copy().save(OUT / "logo-primary.png", "PNG")
recolor(mark.copy(), ROCK, "keep").save(OUT / "logo-reverse.png", "PNG")
recolor(mark.copy(), INK, "hole").save(OUT / "logo-mono-green.png", "PNG")
recolor(mark.copy(), ROCK, "hole").save(OUT / "logo-mono-cream.png", "PNG")

SEAL = (513, 572, 601, 710)                 # 实测印章框 x 513..600 y 572..709
mark.crop((SEAL[0] - X0, SEAL[1] - Y0, SEAL[2] - X0, SEAL[3] - Y0)) \
    .save(OUT / "logo-seal.png", "PNG")
P("seal crop : %dx%d" % (SEAL[2] - SEAL[0], SEAL[3] - SEAL[1]))

# ---- 最细笔画实测（决定最小使用尺寸）----
# alpha>200 剔除抗锯齿过渡带；双向游程（水平测竖线宽 / 垂直测横线粗）
def runs_of(get, n):
    out = []
    run = 0
    for i in range(n):
        if get(i):
            run += 1
        else:
            if 0 < run <= 24:
                out.append(run)
            run = 0
    if 0 < run <= 24:
        out.append(run)
    return out

pm = mark.load()
H, W = mark.height, mark.width
hruns = []
for y in range(H):
    hruns += runs_of(lambda x, y=y: pm[x, y][3] > 200, W)
vruns = []
for x in range(W):
    vruns += runs_of(lambda y, x=x: pm[x, y][3] > 200, H)
runs = sorted(hruns + vruns)
if runs:
    n = len(runs)
    P("")
    P("thin-stroke runs (<25px, alpha>200, H+V), n=%d  (H=%d V=%d)" % (n, len(hruns), len(vruns)))
    for q in (1, 2, 5, 10, 25):
        P("  p%-3d = %d px" % (q, runs[int(n * q / 100.0)]))
    for q in (2, 5, 10):
        thin = runs[int(n * q / 100.0)]
        P("  p%-3d = %d px  -> 占标志宽 %.2f%%  -> 印刷下限(0.20mm) 须 >= %.0f mm"
          % (q, thin, thin * 100.0 / W, 0.2 * W / thin))

P("")
P("=== 色值表（BrandLock v2 口径 · CMYK 为网式换算参考值，非 ICC 分色，印前须打样校准）")
palette = [("松柏绿 PINE", PINE), ("暖米岩石色 ROCK", ROCK), ("朱砂红 CINNABAR", CINNABAR),
           ("黛青黑 DARKBLUE", DARKBLUE), ("深木胡桃色 WALNUT", WALNUT), ("铜金色 BRONZE", BRONZE),
           ("[内部] Logo 墨色 INK", INK), ("[内部] 印章红 SEAL-RED", SEAL_RED),
           ("参考 纯白 WHITE", (255, 255, 255))]
data = {}
for name, rgb in palette:
    c, m, y, k = to_cmyk(rgb)
    hexs = "#%02X%02X%02X" % rgb
    P("  %-22s %s  rgb%-18s C%-3d M%-3d Y%-3d K%-3d" % (name, hexs, str(rgb), c, m, y, k))
    data[name] = {"hex": hexs, "rgb": list(rgb), "cmyk": [c, m, y, k]}
(LOG / "colors.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
P("")
P("assets ->")
for f in sorted(OUT.glob("logo-*.png")):
    P("  %-24s %8.1f KB  %dx%d" % (f.name, f.stat().st_size / 1024,
                                   Image.open(f).width, Image.open(f).height))
rep.close()
