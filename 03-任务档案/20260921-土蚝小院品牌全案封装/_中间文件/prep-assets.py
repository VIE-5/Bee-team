# -*- coding: utf-8 -*-
"""
土蚝小院 · 品牌全案封装 — 素材预处理
------------------------------------------------------------
做两件事：
  1. 把源 PNG 转成适合页面用的 WEBP（长边压到 1800，控制体积）
  2. 实测每张图的「顶部条带 / 底部条带」平均亮度，写 meta.json
     → HTML 据此自动把页眉/页脚文字切成深色或浅色

亮度判据：相对亮度 L = 0.2126R' + 0.7152G' + 0.0722B'（sRGB 线性化后加权）
  条带取图上缘 0~7% 高、下缘 93~100% 高，全宽。
"""
import json
import os
from pathlib import Path

from PIL import Image

SRC = Path(r"E:\唐V-work\土蚝小院\土蚝\LOGO定\土蚝小院视觉资产")
OUT = Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260921-土蚝小院品牌全案封装\01-工蜂产出\assets")
OUT.mkdir(parents=True, exist_ok=True)

MAX_EDGE = 1800
BAND = 0.07          # 上下各取 7% 高
LIGHT_THRESHOLD = 0.55   # 亮度高于此值 → 浅底 → 页眉页脚用深色字


def srgb_to_lin(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(img: Image.Image) -> float:
    """整图平均相对亮度（0=黑 1=白）"""
    small = img.convert("RGB").resize((64, 64), Image.LANCZOS)
    px = list(small.getdata())
    tot = 0.0
    for r, g, b in px:
        tot += (0.2126 * srgb_to_lin(r) + 0.7152 * srgb_to_lin(g) + 0.0722 * srgb_to_lin(b))
    return tot / len(px)


def band_luminance(img: Image.Image, which: str) -> float:
    """条带平均亮度：which = 'top' | 'bottom'"""
    rgb = img.convert("RGB")
    w, h = rgb.size
    bh = max(1, int(h * BAND))
    box = (0, 0, w, bh) if which == "top" else (0, h - bh, w, h)
    return luminance(rgb.crop(box))


# 统一命名：源文件名 → 语义化短名（ASCII，避免中文路径坑）
NAME_MAP = {
    # —— 标志 / 规范 ——
    "logo.png":                                              "logo-primary",
    "logo-白.png":                                            "logo-reverse",
    # —— 品牌平面规范（Codex 系列，16:9） ——
    "Codex 图像 2026年9月19日 18_36_27-2.png":                "std-color",
    "Codex 图像 2026年9月19日 18_36_36-3.png":                "std-graphic",
    "Codex 图像 2026年9月19日 18_36_42-4.png":                "std-lightbox",
    "Codex 图像 2026年9月19日 18_36_52-5.png":                "std-wallculture",
    # —— LOGO 规范（ChatGPT 9/18 系列，16:9） ——
    "ChatGPT Image 2026年9月18日 16_57_17 (1).png":           "logo-concept",
    "ChatGPT Image 2026年9月18日 16_57_20 (3).png":           "logo-color",
    "ChatGPT Image 2026年9月18日 16_57_24 (6).png":           "logo-mono",
    # —— 应用总览（ChatGPT 9/21 系列，4:3） ——
    "ChatGPT Image 2026年9月21日 12_05_34 (4).png":           "ip-wall",
    "ChatGPT Image 2026年9月21日 12_57_54.png":               "kv-slogan-gold",
    # —— 场景应用（4:3） ——
    "品牌文化墙.png":                                          "app-culturewall",
    "品牌故事.png":                                            "app-brandstory",
    "买单.png":                                                "app-membership",
    "入门.png":                                                "app-entrance",
    "用餐.png":                                                "app-tableware",
    "点餐.png":                                                "app-order",
    "外卖.png":                                                "app-takeaway",
    "提示牌.png":                                              "app-signage",
    "slogan体现.png":                                          "app-slogan",
    "灯箱.png":                                                "app-lightbox-1",
    "灯箱-2.png":                                              "app-lightbox-2",
    "横板灯箱.png":                                            "app-lightbox-h",
    "竖版灯箱.png":                                            "app-lightbox-v",
}


def main():
    meta = {}
    missing = []
    for src_name, short in NAME_MAP.items():
        p = SRC / src_name
        if not p.exists():
            missing.append(src_name)
            continue
        im = Image.open(p)
        im.load()
        w, h = im.size

        # —— 转 webp（长边压到 1800）——
        work = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
        scale = min(1.0, MAX_EDGE / max(w, h))
        if scale < 1.0:
            nw, nh = int(round(w * scale)), int(round(h * scale))
            work = work.resize((nw, nh), Image.LANCZOS)
        else:
            nw, nh = w, h

        dst = OUT / f"{short}.webp"
        work.save(dst, "WEBP", quality=88, method=6)

        # —— 亮度实测（在原图分辨率上量，更准）——
        L_all = luminance(im)
        L_top = band_luminance(im, "top")
        L_bot = band_luminance(im, "bottom")

        meta[short] = {
            "src": src_name,
            "file": f"{short}.webp",
            "w": nw, "h": nh,
            "ratio": round(nw / nh, 4),
            "lum_all": round(L_all, 4),
            "lum_top": round(L_top, 4),
            "lum_bottom": round(L_bot, 4),
            "header_on_light": L_top > LIGHT_THRESHOLD,
            "footer_on_light": L_bot > LIGHT_THRESHOLD,
            "kb": round(dst.stat().st_size / 1024, 1),
        }
        print(f"{short:20s} {nw}x{nh}  L_all={L_all:.3f} top={L_top:.3f} "
              f"bot={L_bot:.3f}  hdr={'深字' if L_top > LIGHT_THRESHOLD else '浅字'}  "
              f"{meta[short]['kb']:7.1f}KB")

    (OUT / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print("-" * 72)
    print(f"产出 {len(meta)} 张 webp")
    if missing:
        print(f"[!] 源文件缺失 {len(missing)} 个：")
        for m in missing:
            print("   -", m)
    total = sum(v["kb"] for v in meta.values())
    print(f"总体积 {total/1024:.2f} MB")


if __name__ == "__main__":
    main()
