# -*- coding: utf-8 -*-
"""诊断：精确导出 P05 段（以 <section class="slide"> ... <div class="pg">05</div> 为界）。"""
import io, os, re

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
html = io.open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()
parts = re.split(r'(?=<section class="slide)', html)

for i, chunk in enumerate(parts):
    m = re.search(r'<div class="pg">(\d+)</div>', chunk)
    if m and m.group(1) == '05':
        print('chunk index:', i)
        print('=' * 74)
        print(chunk.strip())
        break
