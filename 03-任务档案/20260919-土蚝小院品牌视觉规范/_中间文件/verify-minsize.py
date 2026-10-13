# -*- coding: utf-8 -*-
"""
verify-minsize.py —— 验证规范册里的「最小尺寸」两条下限是否成立。

印刷侧：由最细结构线宽度反推（数字见 prep.report.txt）。
屏幕侧：规范写的是「320px 时朱印内『土蚝』二字仍可辨认 —— 是实际判据，不是系数推算」，
        那就必须真的缩到 320px 看一眼，不能空口说。
"""
from pathlib import Path
from PIL import Image

ROOT = Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉规范")
A = ROOT / "01-工蜂产出" / "assets"
OUT = ROOT / "_中间文件"
ROCK = (0xE7, 0xDC, 0xC7)

im = Image.open(A / "logo-primary.png").convert("RGBA")
W, H = im.size                      # 785 x 720
# 朱印在标志内的相对框（源图 513..601 / 572..711 减去 mark 原点 449,80）
SEAL_IN_MARK = (64, 492, 152, 631)

rows = []
for target_w in (320, 240, 160):
    s = target_w / float(W)
    sw, sh = target_w, int(round(H * s))
    small = im.resize((sw, sh), Image.LANCZOS)
    x0, y0, x1, y1 = [int(round(v * s)) for v in SEAL_IN_MARK]
    pad = 4
    box = (max(0, x0 - pad), max(0, y0 - pad), min(sw, x1 + pad), min(sh, y1 + pad))
    crop = small.crop(box)
    k = max(1, int(round(320.0 / crop.width)))
    big = crop.resize((crop.width * k, crop.height * k), Image.NEAREST)
    bg = Image.new("RGB", big.size, ROCK)
    bg.paste(big, (0, 0), big)
    f = OUT / ("minsize-seal-%dx.png" % target_w)
    bg.save(f)
    rows.append("w=%-4d 整标 %dx%d  朱印 %.0fx%.0f px  放大%dx -> %s"
                % (target_w, sw, sh, (x1 - x0), (y1 - y0), k, f.name))

# 再拼一张：三种宽度下的整标对比（同底，等比并排）
tiles = []
for target_w in (320, 240, 160):
    s = target_w / float(W)
    sw, sh = target_w, int(round(H * s))
    t = im.resize((sw, sh), Image.LANCZOS)
    bg = Image.new("RGB", (sw, 200), ROCK)
    bg.paste(t, (0, (200 - sh) // 2), t)
    tiles.append(bg)
sheet = Image.new("RGB", (sum(t.width for t in tiles) + 40, 200), ROCK)
x = 0
for t in tiles:
    sheet.paste(t, (x, 0))
    x += t.width + 20
sheet.save(OUT / "minsize-compare.png")

(OUT / "minsize.report.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
print("\n".join(rows))
