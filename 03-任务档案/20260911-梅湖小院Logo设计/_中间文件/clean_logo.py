# -*- coding: utf-8 -*-
"""
T3 附属工具 · 水印检测与裁切补偿  v2
原理：AI 生图模型默认在右下角打「AI生成 WORKBUDDY」水印。
      v2 修正：水印是浅灰细字，行平均值会把差异稀释 → 改用行内「最大差异」检测。
      探测到水印顶边后，裁掉该区域并左右对称裁切保持正方形，再统一放大回 1024x1024。
      不涂抹、不修改任何画面内容。
"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE, "01-工蜂产出")

JOBS = [
    ("Minimalist_circular_emblem_log_2026-09-11T04-22-17.png", "T3-LOGO-A-湖月映梅.png", "skip"),
    ("Extremely_minimal_logo_mark_fo_2026-09-11T04-21-10.png", "T3-LOGO-B-院门鱼跃.png", 71),
    ("Minimalist_Chinese_ink_brush_l_2026-09-11T04-21-24.png", "T3-LOGO-C-梅湖墨韵.png", "auto"),
]

TOL = 30                 # 最大通道差容差（水印灰字与浅底差异约 80-90）
SCAN_X0, SCAN_X1 = 880, 1000   # 水印横向范围（避开画面主体）
REF_BOX = (880, 800, 1000, 860)  # 参考背景取样区（水印正上方的纯背景）


def max_row_diff(px, y, x0, x1, ref):
    worst = 0
    for x in range(x0, x1, 2):
        p = px[x, y]
        d = max(abs(p[0] - ref[0]), abs(p[1] - ref[1]), abs(p[2] - ref[2]))
        if d > worst:
            worst = d
    return worst


def ref_color(px):
    r = g = b = n = 0
    for y in range(REF_BOX[1], REF_BOX[3], 2):
        for x in range(REF_BOX[0], REF_BOX[2], 2):
            p = px[x, y]; r += p[0]; g += p[1]; b += p[2]; n += 1
    return (r / n, g / n, b / n)


def detect_watermark_top(im):
    px = im.load()
    w, h = im.size
    ref = ref_color(px)
    top = None
    blank_run = 0
    for y in range(h - 2, h // 2, -1):
        if max_row_diff(px, y, SCAN_X0, SCAN_X1, ref) > TOL:
            top = y
            blank_run = 0
        else:
            blank_run += 1
            if top is not None and blank_run > 10:
                break
    return top, ref


def main():
    for src_name, dst_name, mode in JOBS:
        path = os.path.join(IMG_DIR, src_name)
        im = Image.open(path).convert("RGB")
        w, h = im.size

        if mode == "skip":
            print(f"[{dst_name}] 免检（已肉眼确认无水印），保持原图 {w}x{h}")
            out = im
        elif isinstance(mode, int):
            # 人工确认有水印但自动检测对比度不足 → 按同模板固定位置裁切
            new_h = h - mode
            side = (w - new_h) // 2
            out = im.crop((side, 0, w - side, new_h))
            print(f"[{dst_name}] 强制裁切（人工确认有水印）→ 裁掉底部 {mode}px，左右各 {side}px → {out.size}")
        else:
            top, ref = detect_watermark_top(im)
            if top is None:
                print(f"[{dst_name}] 未检测到水印，保持原图 {w}x{h}")
                out = im
            else:
                cut = h - (top - 14)
                new_h = h - cut
                side = (w - new_h) // 2
                out = im.crop((side, 0, w - side, new_h))
                print(f"[{dst_name}] 水印顶边 y={top}（背景参考 {tuple(round(c) for c in ref)}）"
                      f" → 裁掉底部 {cut}px，左右各 {side}px → {out.size}")

        if out.size != (1024, 1024):
            out = out.resize((1024, 1024), Image.LANCZOS)
            print(f"          → 复原至 1024x1024")

        dst = os.path.join(IMG_DIR, dst_name)
        out.save(dst, "PNG", optimize=True)
        print(f"          → 已输出 {dst}")


if __name__ == "__main__":
    main()
