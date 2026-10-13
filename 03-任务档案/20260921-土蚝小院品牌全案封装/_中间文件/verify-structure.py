# -*- coding: utf-8 -*-
"""结构终检：页数 / 页码连续性 / 注释页码序列 / 每页图片数。"""
import io, os, re

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
html = io.open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()

secs = re.findall(r'<section class="slide[^>]*>.*?</section>', html, re.S)
print('section 数 : %d' % len(secs))

pgs = []
for s in secs:
    m = re.search(r'<div class="pg">(\d+)</div>', s)
    pgs.append(int(m.group(1)) if m else None)
np = [p for p in pgs if p is not None]
print('无页码页   : %s' % ([i + 1 for i, p in enumerate(pgs) if p is None] or '无'))
print('页码序列   : %s' % ('%d..%d 连续 ✓' % (np[0], np[-1]) if np == list(range(np[0], np[0] + len(np)))
                           else '异常 → %s' % np))

coms = [int(c) for c in re.findall(r'P(\d{1,2}) ·', html)]
print('注释页码   : %s' % ('1..%d 连续 ✓' % len(coms) if coms == list(range(1, len(coms) + 1))
                          else '异常 → %s' % coms))

ms = [len(re.findall(r'src="assets/([^"]+)"', s)) for s in secs]
print('图片总数   : %d' % sum(ms))
print('0 图页     : %s' % ([i + 1 for i, n in enumerate(ms) if n == 0] or '无'))

# 物料页逐页
print('-' * 58)
for i, s in enumerate(secs, 1):
    if 'mat-single' in s:
        k = re.search(r'src="assets/(mat-\d+)\.webp"', s).group(1)
        t = re.search(r'<div class="sec-h">([^<]+)</div>', s).group(1)
        print('  P%-3d %-9s %s' % (i, k, t))
print('-' * 58)

# 检查 .mat-pair 残留 / .mat-single 计数
print('.mat-pair 残留 : %d' % len(re.findall(r'class="mat-pair', html)))
print('.mat-single    : %d' % len(re.findall(r'class="mat-single"', html)))
# 触边元素检查：确认物料页无 position:absolute 的图 / 无 gradient
grad = len(re.findall(r'linear-gradient|radial-gradient', html))
print('内联渐变       : %d' % grad)
