# -*- coding: utf-8 -*-
"""独立物料 → 全册素材规范重制（v5）

规范与 prep-assets-hd.py / replace-assets.py 完全一致：
  长边 1920、LANCZOS、放大时轻度锐化、webp q90。
源图 1448×1086（4:3）→ 1920×1440。

命名 mat-01 … mat-24，映射记入 meta.json。
"""
import json
import os
from pathlib import Path

from PIL import Image, ImageFilter

SRC = Path(r"E:\唐V-work\土蚝小院\土蚝\LOGO定\独立物料")
OUT = Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260921-土蚝小院品牌全案封装\01-工蜂产出\assets")

# ★ 长边目标：**1200**（不是全册通用的 1920）
#   理由（几何核算 + PDF 实测）：
#     物料图在 .mat-pair 中显示宽 = (1060.8-18)/2 = 521.4 CSS px
#     → PDF 中占 521.4 × 0.75 = 391 pt
#     1920 px / (391/72 inch) = 353 dpi —— 过剩 2.4 倍
#     1200 px / (391/72 inch) = 221 dpi —— 印刷优质档，屏幕 2× 亦锐利
#   实测背景：Chrome 打印 PDF 用 /FlateDecode 无损嵌入原始像素且不降采样，
#   素材像素直接线性决定 PDF 体积（v5 首版 129.5MB，超「折中 ~70MB」目标）。
TARGET_LONG = 1200

# 语义标签（仅供 meta 记录 / 页面题注参考）—— 已按逐张目视核实修正
LABELS = [
    "客用餐具", "筷套", "牙签套", "餐巾纸盒",
    "湿巾纸", "打火机", "外带杯/堂食杯", "餐具更多系列",
    "名片", "门头招牌", "玻璃防撞贴", "门帘",
    "优惠券", "会员卡", "订餐卡", "打包盒",
    "打包标签", "打包袋", "礼品袋", "筷套与餐具套装",
    "营业时间牌", "区域牌", "包间门牌", "温馨提示牌",
    "台号牌", "桌面立牌", "员工工牌", "服务员服装", "厨师服装",
]


def linear(v):
    v = v / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminance(img):
    rgb = img.convert("RGB").resize((64, 64), Image.LANCZOS)
    tot = 0.0
    for r, g, b in rgb.getdata():
        tot += 0.2126 * linear(r) + 0.7152 * linear(g) + 0.0722 * linear(b)
    return tot / (64 * 64)


def band_luminance(img, where, h_frac=0.09):
    w, h = img.size
    bh = max(1, int(h * h_frac))
    box = (0, 0, w, bh) if where == "top" else (0, h - bh, w, h)
    return luminance(img.crop(box))


def main():
    fs = sorted(os.listdir(SRC))
    assert len(fs) == len(LABELS), "文件数 %d != LABELS %d" % (len(fs), len(LABELS))
    print('源文件 %d 张' % len(fs))

    meta_p = OUT / "meta.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}

    for i, fn in enumerate(fs, 1):
        p = SRC / fn
        key = "mat-%02d" % i
        im = Image.open(p)
        w0, h0 = im.size
        scale = TARGET_LONG / max(w0, h0)
        w1, h1 = int(round(w0 * scale)), int(round(h0 * scale))
        upscaled = scale > 1.0

        im = im.convert("RGB").resize((w1, h1), Image.LANCZOS)
        if upscaled:
            im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=2))
        out = OUT / f"{key}.webp"
        im.save(out, "WEBP", quality=90, method=6)

        lt, lb = band_luminance(im, "top"), band_luminance(im, "bottom")
        meta[key] = {
            "src": fn,
            "label": LABELS[i - 1],
            "file": f"{key}.webp",
            "w": w1, "h": h1,
            "ratio": round(w1 / h1, 4),
            "src_w": w0, "src_h": h0,
            "upscaled": upscaled,
            "lum_all": round(luminance(im), 4),
            "lum_top": round(lt, 4),
            "lum_bottom": round(lb, 4),
            "header_on_light": lt > 0.55,
            "footer_on_light": lb > 0.55,
            "kb": round(out.stat().st_size / 1024, 1),
            "batch": "materials-v5",
        }
        print("[%02d] %-12s %-8s %dx%d -> %dx%d %s %6.0fKB"
              % (i, key, LABELS[i - 1], w0, h0, w1, h1,
                 "UP" if upscaled else "  ", meta[key]["kb"]))

    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nmeta.json keys = %d" % len(meta))


if __name__ == "__main__":
    main()
