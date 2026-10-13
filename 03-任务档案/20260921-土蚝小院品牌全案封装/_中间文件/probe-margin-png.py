# -*- coding: utf-8 -*-
"""探针：量 P05 / P27 / P29 / P34 四页的图片实际渲染框与内容区留白。
用 Chrome headless --dump-dom 拿不到几何，改用注入脚本截图前的 DOM 读取：
这里直接用 Chrome 的 --headless + --virtual-time-budget 配合 JS 打印。
简化方案：用 --screenshot 不可取，改用 --dump-dom 无法拿 rect。
→ 改用 Chrome DevTools Protocol 太重；改为渲染后直接量 PNG 的墨迹 bbox。
"""
from PIL import Image, ImageChops
import os

PNG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出', 'png')

for pg in [5, 27, 29, 34]:
    p = os.path.join(PNG, 'slide-%d.png' % pg)
    im = Image.open(p).convert('RGB')
    W, H = im.size
    # 与纯白做差，求非白 bbox
    bg = Image.new('RGB', im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg).convert('L')
    bbox = diff.point(lambda v: 255 if v > 12 else 0).getbbox()
    if bbox:
        l, t, r, b = bbox
        print('P%02d  %dx%d  墨迹bbox=(%d,%d,%d,%d)  上留白=%.1f%%  下留白=%.1f%%  右留白=%.1f%%'
              % (pg, W, H, l, t, r, b,
                 t / H * 100, (H - b) / H * 100, (W - r) / W * 100))
