# -*- coding: utf-8 -*-
"""检查 index.html 当前状态：section 数、页码序列、注释页码。"""
import io, os, re

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
html = io.open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()

secs = re.findall(r'<section class="slide[^>]*>.*?</section>', html, re.S)
print('section 数:', len(secs))
print('-' * 60)
for i, s in enumerate(secs, 1):
    m = re.search(r'<div class="pg">(\d+)</div>', s)
    cls = re.match(r'<section class="slide([^"]*)"', s)
    imgs = re.findall(r'src="assets/([^"]+)"', s)
    print('%2d  pg=%-5s class="%-12s" imgs=%s'
          % (i, m.group(1) if m else 'NONE', cls.group(1).strip(), imgs))
print('-' * 60)
coms = re.findall(r'P(\d{1,2}) ·', html)
print('注释页码序列:', ','.join(coms))
