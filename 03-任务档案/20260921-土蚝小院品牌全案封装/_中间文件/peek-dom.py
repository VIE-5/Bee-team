# -*- coding: utf-8 -*-
"""导出 P05 / P27 / P29 / P34 四页的完整 DOM 片段，供确认排版方式。"""
import io, os, re

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
html = io.open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()
parts = re.split(r'(?=<section class="slide)', html)

TARGETS = {
    'assets/app-brandstory.webp': 'P05',
    'assets/ip-wall.webp': 'P27',
    'assets/std-lightbox.webp': 'P29',
    'assets/app-slogan.webp': 'P34',
}
out = []
for p in parts:
    for key, tag in TARGETS.items():
        if 'src="%s"' % key in p and '<img' in p:
            out.append('=' * 78)
            out.append('### %s   (%s)' % (tag, key))
            out.append('=' * 78)
            out.append(p.strip()[:2600])
            out.append('')
            break

io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_peek-out.txt'),
        'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('written, lines =', len('\n'.join(out).split('\n')))
