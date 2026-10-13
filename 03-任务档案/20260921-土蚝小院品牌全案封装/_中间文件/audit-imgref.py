# -*- coding: utf-8 -*-
"""核对图片引用：出现次数 vs 唯一数，找重复引用。"""
import io, os, re, collections

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
h = io.open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()

srcs = re.findall(r'src="assets/([^"]+)"', h)
c = collections.Counter(srcs)
print('出现次数 : %d' % len(srcs))
print('唯一数   : %d' % len(c))
rep = {k: v for k, v in c.items() if v > 1}
print('重复引用 : %s' % (rep if rep else '无'))

# 仅 img 标签
imgs = re.findall(r'<img[^>]+src="assets/([^"]+)"', h)
print('img 标签数: %d' % len(imgs))
# CSS background 引用
bg = re.findall(r'url\([\'"]?assets/([^\'")]+)', h)
print('CSS 背景数: %d  %s' % (len(bg), sorted(set(bg))))

# 磁盘素材文件
ad = os.path.join(BASE, 'assets')
fs = sorted(f for f in os.listdir(ad) if f.lower().endswith('.webp'))
print('assets/*.webp 文件数: %d' % len(fs))
used = set(c)
orphan = [f for f in fs if f not in used]
print('未被引用: %s' % (orphan if orphan else '无'))
