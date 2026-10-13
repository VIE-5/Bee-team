# -*- coding: utf-8 -*-
"""素材高清重制 · 替换版（v4）
把主人新上传的四张附件，按既有规范重制后覆盖对应素材：
  P05 -> app-brandstory.webp
  P27 -> ip-wall.webp
  P29 -> std-lightbox.webp
  P34 -> app-slogan.webp
规范与 prep-assets-hd.py 完全一致：长边 1920、LANCZOS、轻度锐化、webp q90。
"""
import json
import os
import shutil
from pathlib import Path

from PIL import Image, ImageFilter

SRC = Path(r"C:\Users\27612\.workbuddy\clipboard-images")
OUT = Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260921-土蚝小院品牌全案封装\01-工蜂产出\assets")
BAK = OUT / "_bak-v3"

TARGET_LONG = 1920

REPLACE = [
    ("clipboard-2026-09-21T10-09-11-146Z-fa7da6db.jpg", "app-brandstory", "P05"),
    ("clipboard-2026-09-21T10-09-11-150Z-826f79d7.jpg", "ip-wall",         "P27"),
    ("clipboard-2026-09-21T10-09-11-163Z-996356c2.jpg", "std-lightbox",    "P29"),
    ("clipboard-2026-09-21T10-09-11-160Z-3d988465.jpg", "app-slogan",      "P34"),
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
    BAK.mkdir(parents=True, exist_ok=True)

    meta_p = OUT / "meta.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}

    for src_name, key, tag in REPLACE:
        p = SRC / src_name
        if not p.exists():
            print("[MISS]", src_name)
            continue

        # 备份旧素材（只备一次）
        old = OUT / f"{key}.webp"
        b = BAK / f"{key}.webp"
        if old.exists() and not b.exists():
            shutil.copy2(old, b)
            print("  backup -> _bak-v3/%s.webp" % key)

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
            "src": src_name,
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
            "replaced_v4": tag,
        }
        print("[OK] %-4s %-16s %dx%d -> %dx%d %s  %7.1fKB"
              % (tag, key, w0, h0, w1, h1, "UP" if upscaled else "  ", meta[key]["kb"]))

    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nmeta.json updated, keys =", len(meta))


if __name__ == "__main__":
    main()
