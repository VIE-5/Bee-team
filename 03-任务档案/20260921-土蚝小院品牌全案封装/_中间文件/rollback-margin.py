# -*- coding: utf-8 -*-
"""回滚误改：P15 / P16 / P26 三页的标题行 margin-bottom 由 14px 恢复为 20px。
只动这三页，其余（P27/P29/P34）保持 14px。
"""
import io, os, re

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
p = os.path.join(BASE, 'index.html')
html = io.open(p, encoding='utf-8').read()

TARGETS = {'15', '16', '26'}
parts = re.split(r'(?=<section class="slide)', html)

fixed, touched = 0, []
for i, chunk in enumerate(parts):
    if chunk.startswith('<section class="slide') is False:
        continue
    m = re.search(r'<div class="pg">(\d+)</div>', chunk)
    if not m or m.group(1) not in TARGETS:
        continue
    pg = m.group(1)
    new = chunk.replace(
        'align-items:flex-end;margin-bottom:14px">',
        'align-items:flex-end;margin-bottom:20px">')
    if new != chunk:
        parts[i] = new
        fixed += 1
        touched.append(pg)

io.open(p, 'w', encoding='utf-8', newline='\n').write(''.join(parts))
print('restored pages:', touched, 'count =', fixed)
