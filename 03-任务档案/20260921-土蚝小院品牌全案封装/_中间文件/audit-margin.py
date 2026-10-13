# -*- coding: utf-8 -*-
"""查明被改成 margin-bottom:14px 的全部 6 处属哪几页（应只有 P27/P29/P34 三页）。"""
import io, os, re

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
html = io.open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()
parts = re.split(r'(?=<section class="slide)', html)

for i, p in enumerate(parts):
    if 'margin-bottom:14px' in p:
        m = re.search(r'<div class="pg">(\d+)</div>', p)
        pg = m.group(1) if m else '?'
        mcls = re.match(r'<section class="slide([^"]*)"', p)
        print('chunk %-3s  pg=%-4s class="%s"' % (i, pg, mcls.group(1).strip() if mcls else ''))
        # 打印标题行原文
        for mm in re.finditer(r'<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:(\d+)px">', p):
            print('      ->', mm.group(0)[:120])
