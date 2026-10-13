# -*- coding: utf-8 -*-
"""诊断：四页 img 标签的真实原文。"""
import io, os, re

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
html = io.open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()

for key in ['app-brandstory', 'ip-wall', 'std-lightbox', 'app-slogan']:
    for m in re.finditer(r'<img[^>]*src="assets/%s\.webp"[^>]*>' % key, html):
        print('>>> %s' % key)
        print(repr(m.group(0)))
        print()
