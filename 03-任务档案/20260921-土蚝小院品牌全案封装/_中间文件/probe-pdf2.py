# -*- coding: utf-8 -*-
"""探测 PDF 内嵌图像：数量 / 尺寸 / 编码方式 / 压缩后字节占比。
用于定位 v5 PDF 体积（129.5MB）的来源。
"""
import os
import re
import sys
from collections import Counter

p = sys.argv[1]
b = open(p, 'rb').read()
print('PDF: %s  %.1f MB' % (os.path.basename(p), len(b) / 1048576))
print('-' * 66)

# 图像对象
objs = re.findall(rb'<<(?:[^<>]|<<[^>]*>>)*?/Subtype\s*/Image(?:[^<>]|<<[^>]*>>)*?>>', b, re.S)
print('图像对象数:', len(objs))

filters = Counter()
sizes = []
for o in objs:
    f = re.search(rb'/Filter\s*(?:/\w+|\[[^\]]*\])', o)
    filters[f.group(0).decode('ascii', 'replace') if f else 'NONE'] += 1
    w = re.search(rb'/Width\s+(\d+)', o)
    h = re.search(rb'/Height\s+(\d+)', o)
    if w and h:
        sizes.append((int(w.group(1)), int(h.group(1))))

print('Filter 分布:')
for k, v in filters.most_common():
    print('   %-46s %d' % (k, v))

if sizes:
    sizes.sort(key=lambda t: -(t[0] * t[1]))
    print('图像尺寸 Top8（按像素数）:')
    for w, h in sizes[:8]:
        print('   %5d x %-5d' % (w, h))
    c = Counter(sizes)
    print('尺寸分布 Top8:')
    for (w, h), n in c.most_common(8):
        print('   %5d x %-5d  x%d' % (w, h, n))

# 流对象总字节（粗估）
streams = re.findall(rb'stream\r?\n(.*?)\r?\nendstream', b, re.S)
tot = sum(len(s) for s in streams)
print('-' * 66)
print('stream 总字节: %.1f MB  (占文件 %.0f%%)' % (tot / 1048576, tot / len(b) * 100))
print('最大 stream: %.2f MB' % (max((len(s) for s in streams), default=0) / 1048576))
