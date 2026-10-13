# -*- coding: utf-8 -*-
"""按新素材比例重设四页的图片尺寸约束（几何预算）。

内容区：left/right = --mx(149.6)，top = --hdr(127.5)，bottom = 10% (85)
→ 内容区 1060.8 x 637.5；P27/29/34 顶部标题行约 82px → 大图可用高 ≈ 555px

几何结论：
  P05 app-brandstory  4:3  → c-split w64 图列宽 406.7px → 高 305px（宽决定）
  P27 ip-wall         16:9 → 全宽 1060.8 时高 597 > 555 → 按高限 555
  P29 std-lightbox    4:3  → 全宽时高 795.6 > 555 → 按高限 555
  P34 app-slogan      4:3  → 同 P29
"""
import io, os

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
p = os.path.join(BASE, 'index.html')
s = io.open(p, encoding='utf-8').read()
orig_len = len(s)

REPL = [
    # (tag, old, new)
    ('P05',
     '<img src="assets/app-brandstory.webp" style="max-height:512px" alt="品牌故事呈现">',
     '<img src="assets/app-brandstory.webp" style="width:100%;height:auto;object-fit:contain" alt="品牌故事呈现">'),

    ('P27',
     '<img src="assets/ip-wall.webp" style="width:100%;max-height:530px;object-fit:contain;border:1px solid var(--line)" alt="插画IP规划与墙面展示">',
     '<img src="assets/ip-wall.webp" style="width:100%;height:auto;max-height:555px;object-fit:contain;object-position:center;border:1px solid var(--line)" alt="插画IP规划与墙面展示">'),

    ('P29',
     '<img src="assets/std-lightbox.webp" style="width:100%;max-height:520px;object-fit:contain;border:1px solid var(--line)" alt="KV灯箱规范">',
     '<img src="assets/std-lightbox.webp" style="width:100%;height:auto;max-height:555px;object-fit:contain;object-position:center;border:1px solid var(--line)" alt="KV灯箱规范">'),

    ('P34',
     '<img src="assets/app-slogan.webp" style="width:100%;max-height:520px;object-fit:contain;border:1px solid var(--line)" alt="Slogan广告语呈现">',
     '<img src="assets/app-slogan.webp" style="width:100%;height:auto;max-height:555px;object-fit:contain;object-position:center;border:1px solid var(--line)" alt="Slogan广告语呈现">'),
]

for tag, old, new in REPL:
    n = s.count(old)
    if n != 1:
        print('[FAIL] %s  match=%d' % (tag, n))
        continue
    s = s.replace(old, new)
    print('[OK]   %s' % tag)

# 三页标题行 margin-bottom 由 18/20 收到 14，给大图让出高度
a = s.count('<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:18px">')
b = s.count('<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:20px">')
s = s.replace('<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:18px">',
              '<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:14px">')
s = s.replace('<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:20px">',
              '<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:14px">')
print('title-row margins: 18px x%d, 20px x%d -> 14px' % (a, b))

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('file len %d -> %d' % (orig_len, len(s)))
