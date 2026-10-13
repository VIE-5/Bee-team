# -*- coding: utf-8 -*-
"""
PPTX 几何探针 —— 验证每张图片的宽高比与源图**完全一致**（零变形），并列出落位。

用法：
    python probe-pptx.py <file.pptx>

为什么需要它：
    PDF 侧探针（PyMuPDF get_image_info）的 bbox 含抗锯齿过渡带，会系统性外扩（实测约 4.2px），
    不能当几何判据。而 **pptx 里存的是设计值本身** —— 直接量宽高比，能一次性判定
    「有没有被拉伸」，比渲染后扫描更直接、更快。
    两者配合：本探针判「变形」，PDF 像素扫描判「色值与边界」。
"""
import sys

from pptx import Presentation

PXU = 9525.0


def main(path):
    prs = Presentation(path)
    bad = 0
    n_pic_all = 0
    print(f'画布 {prs.slide_width / PXU:.1f} x {prs.slide_height / PXU:.1f} px')
    for i, slide in enumerate(prs.slides, 1):
        pics, txts, shps = [], 0, 0
        for sh in slide.shapes:
            if sh.__class__.__name__ == 'Picture':
                pics.append(sh)
            elif sh.has_text_frame and sh.text_frame.text.strip():
                txts += 1
            elif sh.shape_type is not None:
                shps += 1
        if not pics:
            print(f'\n=== P{i} ===  (无图片 · 文本框 {txts} / 形状 {shps})')
            continue
        print(f'\n=== P{i} ===')
        for sh in pics:
            n_pic_all += 1
            iw, ih = sh.image.size
            w, h = sh.width / PXU, sh.height / PXU
            x, y = sh.left / PXU, sh.top / PXU
            r_src, r_put = iw / ih, w / h
            d = abs(r_src - r_put)
            if d >= 0.002:
                bad += 1
            print(f'  [图] 源 {iw}x{ih} 比 {r_src:.4f} | 落位 x={x:7.1f} y={y:7.1f} '
                  f'{w:7.1f}x{h:7.1f} 比 {r_put:.4f}  {"OK" if d < 0.002 else "BAD 变形!"}')
        print(f'  图片 {len(pics)} / 文本框 {txts} / 形状 {shps}')
    print(f'\n图片合计 {n_pic_all} 张，宽高比失配数 = {bad}'
          f'  {"（全部零变形）" if bad == 0 else "（需修）"}')
    return 0 if bad == 0 else 2


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
