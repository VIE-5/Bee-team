# -*- coding: utf-8 -*-
"""导出 V4 中 P17~P27（器物/空间应用段落）的 DOM，确认图位结构。"""
import io, os, re

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
html = io.open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()
parts = re.split(r'(?=<section class="slide)', html)

out = []
for i, chunk in enumerate(parts):
    m = re.search(r'<div class="pg">(\d+)</div>', chunk)
    if not m:
        continue
    pg = int(m.group(1))
    if 17 <= pg <= 28:
        cls = re.match(r'<section class="slide([^"]*)"', chunk)
        imgs = re.findall(r'src="assets/([^"]+)"', chunk)
        out.append('#' * 76)
        out.append('### P%02d   class="%s"   imgs=%s' % (pg, cls.group(1).strip() if cls else '', imgs))
        out.append('#' * 76)
        out.append(chunk.strip())
        out.append('')

io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_peek-app.txt'),
        'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('lines =', len('\n'.join(out).split('\n')))
