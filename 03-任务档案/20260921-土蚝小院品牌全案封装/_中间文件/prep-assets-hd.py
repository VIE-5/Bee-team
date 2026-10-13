# -*- coding: utf-8 -*-
"""
prep-assets-hd.py —— 素材高清重制（v2）

目的（主人 2026-09-21 追加要求）：
  「所有 PDF 中的字体与英文进行统一优化，文字要清晰，图片要高清。」

高清判据（本轮定）：
  PDF 画布 1360×850 CSS px（= 1020×637.5pt @96dpi）。
  页面内图片展示宽度最大 ≈ 990 CSS px（c-split 图列 w46：1060.8 × 1.5/2.5 = 636px；
  满幅页 = 1360px；std-* 规范页 = 1060.8px）。
  → **素材长边必须 ≥ 2 × 最大展示尺寸**，即满幅页 1360×2 = **2720**。
  故统一压到长边 **2720**（16:9 → 2720×1530；4:3 → 2720×2040；竖版 → 2040×2720），
  超出源尺寸的一律 **LANCZOS 放大**（源是矢量级稿件，放大后锐度可接受，
  好过在 PDF 里被浏览器做低质量插值）。

同时输出 `meta.json`：每张图的顶部/底部条带亮度（供 CSS 自动切页眉页脚字色）。
"""
import json
from pathlib import Path

from PIL import Image, ImageFilter

SRC_DIR = Path(r"E:\唐V-work\土蚝小院\土蚝\LOGO定\土蚝小院视觉资产")
OUT = Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260921-土蚝小院品牌全案封装\01-工蜂产出\assets")
OUT.mkdir(parents=True, exist_ok=True)

# 长边目标
#   v2 初版取 2720（= 2× 满幅展示宽 1360）→ PDF 实测 144.5 MB，对交付过于笨重。
#   主人 2026-09-21 拍板走折中：**1920 长边**，等效 135dpi —
#   屏幕浏览锐利、印刷可接受，PDF 落在 ~70 MB。
#   ⚠️ 文字清晰度与此无关：Chrome 导出 PDF 时文字**始终是矢量**（实测字体对象 389 个），
#      PDF 体积差异 100% 来自图片分辨率。
TARGET_LONG = 1920

# 中文名 -> ASCII 短名
NAME_MAP = {
    "品牌文化墙.png": "app-culturewall",
    "品牌故事.png": "app-brandstory",
    "买单.png": "app-membership",
    "入门.png": "app-entrance",
    "用餐.png": "app-tableware",
    "点餐.png": "app-order",
    "外卖.png": "app-takeaway",
    "提示牌.png": "app-signage",
    "slogan体现.png": "app-slogan",
    "灯箱.png": "app-lightbox-1",
    "灯箱-2.png": "app-lightbox-2",
    "横板灯箱.png": "app-lightbox-h",
    "竖版灯箱.png": "app-lightbox-v",
    "Codex 图像 2026年9月19日 18_36_27-2.png": "std-color",
    "Codex 图像 2026年9月19日 18_36_36-3.png": "std-graphic",
    "Codex 图像 2026年9月19日 18_36_42-4.png": "std-lightbox",
    "Codex 图像 2026年9月19日 18_36_52-5.png": "std-wallculture",
    "ChatGPT Image 2026年9月18日 16_57_17 (1).png": "logo-concept",
    "ChatGPT Image 2026年9月18日 16_57_20 (3).png": "logo-color",
    "ChatGPT Image 2026年9月18日 16_57_24 (6).png": "logo-mono",
    "ChatGPT Image 2026年9月21日 12_05_34 (4).png": "ip-wall",
    "ChatGPT Image 2026年9月21日 12_57_54.png": "kv-slogan-gold",
}


def linear(v):
    v = v / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminance(img):
    """sRGB 相对亮度（线性化后按 Rec.709 权重）"""
    rgb = img.convert("RGB").resize((64, 64), Image.LANCZOS)
    px = list(rgb.getdata())
    tot = 0.0
    for r, g, b in px:
        tot += 0.2126 * linear(r) + 0.7152 * linear(g) + 0.0722 * linear(b)
    return tot / len(px)


def band_luminance(img, where, h_frac=0.09):
    """量顶部/底部条带的平均亮度"""
    w, h = img.size
    bh = max(1, int(h * h_frac))
    box = (0, 0, w, bh) if where == "top" else (0, h - bh, w, h)
    return luminance(img.crop(box))


def main():
    metas = {}
    done = []
    for src_name, key in NAME_MAP.items():
        p = SRC_DIR / src_name
        if not p.exists():
            print(f"[MISS] {src_name}")
            continue
        im = Image.open(p)
        w0, h0 = im.size

        # 长边缩放到 TARGET_LONG（放大用 LANCZOS + 轻微锐化补偿）
        scale = TARGET_LONG / max(w0, h0)
        w1, h1 = int(round(w0 * scale)), int(round(h0 * scale))
        upscaled = scale > 1.0

        if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
            im = im.convert("RGBA")
            im = im.resize((w1, h1), Image.LANCZOS)
            if upscaled:
                # 只锐化 RGB，不碰 alpha
                rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=2))
                im = Image.merge("RGBA", (*rgb.split(), im.getchannel("A")))
            out = OUT / f"{key}.webp"
            im.save(out, "WEBP", quality=90, method=6)
            base = im
        else:
            im = im.convert("RGB").resize((w1, h1), Image.LANCZOS)
            if upscaled:
                im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=2))
            out = OUT / f"{key}.webp"
            im.save(out, "WEBP", quality=90, method=6)
            base = im

        lt, lb = band_luminance(base, "top"), band_luminance(base, "bottom")
        metas[key] = {
            "src": src_name,
            "file": f"{key}.webp",
            "w": w1, "h": h1,
            "ratio": round(w1 / h1, 4),
            "src_w": w0, "src_h": h0,
            "upscaled": upscaled,
            "lum_all": round(luminance(base), 4),
            "lum_top": round(lt, 4),
            "lum_bottom": round(lb, 4),
            "header_on_light": lt > 0.55,
            "footer_on_light": lb > 0.55,
            "kb": round(out.stat().st_size / 1024, 1),
        }
        done.append(key)
        print(f"[OK] {key:18s} {w0}x{h0} -> {w1}x{h1} {'UP' if upscaled else '  '}  {metas[key]['kb']:7.1f}KB")

    (OUT / "meta.json").write_text(json.dumps(metas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\ntotal {len(done)} assets -> {OUT}")


if __name__ == "__main__":
    main()
