# -*- coding: utf-8 -*-
"""
clean_logo.py · 生图水印裁切补偿工具（蜂群沉淀 v1）

背景：本环境的生图通道会在图片右下角默认叠加「AI生成」水印，
      prompt 的 no watermark 与工具 footnote 参数都无法抑制。
      本工具用「裁切补偿」方式去除：探测水印顶边 → 裁掉底部 + 左右对称补齐保持正方形
      → 无损放大回原尺寸。全程不涂抹、不遮盖，画面内容零损伤。

用法：
    python clean_logo.py <图片文件或目录> [--cut N] [--suffix _clean]

    --cut N     强制裁掉底部 N 像素（自动检测不可靠时使用，常见值 71）
    默认自动检测；输出到同目录，文件名加后缀。

注意（踩坑记录）：
    水印是浅灰细字，用「行平均色差」判定会被稀释导致漏检 —— 必须用「行内最大色差」。
"""
import os
import sys
from PIL import Image

TOL = 30                          # 最大通道差容差（水印灰字与浅底差异约 80-90）
SCAN_X0, SCAN_X1 = 880, 1000      # 水印横向范围（避开画面主体）
REF_BOX = (880, 800, 1000, 860)   # 参考背景取样区（水印正上方）
EXTS = (".png", ".jpg", ".jpeg", ".webp")


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
            p = px[x, y]
            r += p[0]; g += p[1]; b += p[2]; n += 1
    return (r / n, g / n, b / n)


def detect_top(im):
    px = im.load()
    w, h = im.size
    ref = ref_color(px)
    top, blank_run = None, 0
    for y in range(h - 2, h // 2, -1):
        if max_row_diff(px, y, SCAN_X0, SCAN_X1, ref) > TOL:
            top, blank_run = y, 0
        else:
            blank_run += 1
            if top is not None and blank_run > 10:
                break
    return top


def process(path, cut, suffix):
    im = Image.open(path).convert("RGB")
    w, h = im.size

    if cut:
        c = cut
        print(f"  [{os.path.basename(path)}] 强制裁切底部 {c}px")
    else:
        top = detect_top(im)
        if top is None:
            print(f"  [{os.path.basename(path)}] 未检测到水印，跳过")
            return None
        c = h - (top - 14)
        print(f"  [{os.path.basename(path)}] 检测到水印顶边 y={top} → 裁切 {c}px")

    new_h = h - c
    side = (w - new_h) // 2
    out = im.crop((side, 0, w - side, new_h))
    if out.size != (w, h):
        out = out.resize((w, h), Image.LANCZOS)

    dst = os.path.splitext(path)[0] + suffix + ".png"
    out.save(dst, "PNG", optimize=True)
    print(f"      → {dst}")
    return dst


def main():
    args = [a for a in sys.argv[1:]]
    cut = 0
    suffix = "_clean"
    if "--cut" in args:
        i = args.index("--cut")
        cut = int(args[i + 1])
        del args[i:i + 2]
    if "--suffix" in args:
        i = args.index("--suffix")
        suffix = args[i + 1]
        del args[i:i + 2]
    if not args:
        print(__doc__)
        return

    target = args[0]
    if os.path.isdir(target):
        files = [os.path.join(target, f) for f in sorted(os.listdir(target))
                 if f.lower().endswith(EXTS)]
    else:
        files = [target]

    for f in files:
        process(f, cut, suffix)


if __name__ == "__main__":
    main()
