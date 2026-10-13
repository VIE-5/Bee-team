# -*- coding: utf-8 -*-
"""
make-logo-variants.py —— 从官方标志源生成确定性四件套（v2 · 高清）

源判读（2026-09-21 实测 + 白底/深底对照图确认）：
  `logo-白.png` (1671×941 RGBA) —— 真身是**透明底墨色标志**（书法墨迹 + 印章红）。
                白底上完美，深底上不可见。文件名里的"白"指的是白底稿。
                实测像素特征：可见像素 9.97%，alpha 近乎二值（0 桶 15.7 万 / 224 桶 1.58 万，
                中间桶各仅约 300）→ **矢量级平涂稿，无渐变层次**。
                主墨色 bucket (24,48,24) ≈ #2D301B（深墨绿，非纯黑）；印章红 (216,24,24) ≈ #DE1C19。
  `logo.png`    (1672×941 RGB)  —— 深绿底 + 米白标志的**成品展示图**，
                带底色、边缘有暗角，不适合直接贴版。

产出（v2 新增 logo-ink）：
  logo-ink      墨稿原样（**保留 logo-白.png 的原始墨绿 #2D301B + 印章红**）→ 主人指定用于 P10/P11
  logo-primary  墨稿（颜色归一化到官方墨 #2D301B + 印章红 #DE1C19）→ 浅底用
  logo-reverse  反白稿（**双色互换**：墨部→暖白 #F3E8D2，印章红保留）→ 深底用
  logo-mono     单色墨稿（墨迹全转墨，印章也转墨）→ 黑白印刷用

⚠️ BrandLock v2 §2：反白稿必须双色互换，禁止把可见像素整体涂白
   （涂白 = 一坨无结构白剪影，门头/围裙/名片上全废）。

高清：长边统一 2720（= 2 × PDF 满幅展示宽 1360），LANCZOS 放大 + 轻度锐化。
"""
from pathlib import Path

from PIL import Image, ImageFilter

SRC = Path(r"E:\唐V-work\土蚝小院\土蚝\LOGO定\土蚝小院视觉资产\logo-白.png")
OUT = Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260921-土蚝小院品牌全案封装\01-工蜂产出\assets")
OUT.mkdir(parents=True, exist_ok=True)

INK = (0x2D, 0x30, 0x1B)      # 官方墨色
RED = (0xDE, 0x1C, 0x19)      # 官方印章红
CREAM = (0xF3, 0xE8, 0xD2)    # 反白稿暖白

LONG = 1920                    # 长边目标（主人 2026-09-21 拍板折中档，与 prep-assets-hd 一致）
A_MIN = 60                     # alpha 低于此值视为全透明（抗锯齿噪点）


def upscale_sharp(img):
    """长边放大到 LONG，用 LANCZOS；放大后对 RGB 轻锐化（不碰 alpha）。"""
    w, h = img.size
    sc = LONG / max(w, h)
    w1, h1 = int(round(w * sc)), int(round(h * sc))
    img = img.resize((w1, h1), Image.LANCZOS)
    if sc > 1.0:
        rgb = img.convert("RGB").filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=2))
        img = Image.merge("RGBA", (*rgb.split(), img.getchannel("A")))
    return img


def crop_a(img):
    bb = img.split()[-1].getbbox()
    return img.crop(bb) if bb else img


def save(img, name):
    dst = OUT / f"{name}.webp"
    img.save(dst, "WEBP", quality=90, method=6)
    print(f"  -> {name}.webp  {img.size[0]}x{img.size[1]}  {dst.stat().st_size/1024:.1f}KB")


def main():
    im = Image.open(SRC).convert("RGBA")
    w, h = im.size
    px = im.load()
    print(f"源 {SRC.name} {w}x{h}")

    ink = Image.new("RGBA", (w, h), (0, 0, 0, 0))    # 墨稿原样
    prim = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rev = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    mono = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    p_i, p_p, p_r, p_m = ink.load(), prim.load(), rev.load(), mono.load()

    n_red = n_ink = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < A_MIN:
                continue
            # 按 alpha 归一化反算原色（抗锯齿边缘取真实色）
            if a < 255 and a > 0:
                f = 255.0 / a
                r = min(255, int(r * f)); g = min(255, int(g * f)); b = min(255, int(b * f))
            is_red = r > 130 and g < 100 and b < 100
            orig = (r, g, b, a)

            if is_red:
                n_red += 1
                p_i[x, y] = orig                 # ★ 墨稿原样：保留源色
                p_p[x, y] = (*RED, 255)
                p_r[x, y] = (*RED, 255)          # 反白稿保留红（识别点）
                p_m[x, y] = (*INK, a)            # 单色稿转墨
            else:
                n_ink += 1
                p_i[x, y] = orig                 # ★ 墨稿原样
                p_p[x, y] = (*INK, 255)
                p_r[x, y] = (*CREAM, 255)        # ★ 双色互换：墨→暖白
                p_m[x, y] = (*INK, 255)

    tot = w * h
    print(f"  墨迹 {n_ink*100/tot:.1f}%  印章红 {n_red*100/tot:.2f}%")

    for name, img in [("logo-ink", ink), ("logo-primary", prim),
                      ("logo-reverse", rev), ("logo-mono", mono)]:
        save(upscale_sharp(crop_a(img)), name)

    # —— 目视核对图：墨稿/反白稿 × 白底/深底 四格 ——
    chk = Image.new("RGB", (2 * 560 + 30, 2 * 320 + 30), (190, 190, 190))
    for i, (nm, img) in enumerate([("ink 墨稿原样", crop_a(ink)), ("reverse 反白稿", crop_a(rev))]):
        for j, bg in enumerate([(255, 255, 255), (26, 32, 11)]):
            base = Image.new("RGB", img.size, bg)
            base.paste(img, (0, 0), img)
            th = 300
            base = base.resize((int(base.width * th / base.height), th), Image.LANCZOS)
            chk.paste(base, (10 + i * 560, 10 + j * 320))
    p = OUT.parent.parent / "_中间文件" / "_logo-variants-check.png"
    chk.save(p)
    print(f"  核对图 -> {p}")


if __name__ == "__main__":
    main()
