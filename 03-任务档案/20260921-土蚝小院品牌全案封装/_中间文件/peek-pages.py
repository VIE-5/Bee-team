# -*- coding: utf-8 -*-
"""查看 index.html 中 P05 / P27 / P29 / P34 四页的 DOM 结构。"""
import io, os, re, sys

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
html = io.open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()

# 按 <section class="slide ..."> 切分
parts = re.split(r'(?=<section class="slide)', html)
print('total chunks:', len(parts))
for i, p in enumerate(parts):
    m = re.match(r'<section class="slide([^"]*)"', p)
    if not m:
        continue
    cls = m.group(1).strip()
    # 该 chunk 里的 img 引用
    imgs = re.findall(r'<img[^>]*src="([^"]+)"', p)
    head = p[:200].replace('\n', ' ')
    print('--- chunk %d  class="%s"' % (i, cls))
    print('    imgs:', imgs)
