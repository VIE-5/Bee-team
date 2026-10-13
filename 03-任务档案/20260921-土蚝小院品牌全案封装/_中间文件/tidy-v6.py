# -*- coding: utf-8 -*-
"""收尾：清 _pages 临时页；把旧版 PDF 归档进 _旧版/，交付目录只留 v6。"""
import os
import shutil

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
OLD = os.path.join(BASE, '_旧版')

# 1) 清临时页目录
p = os.path.join(BASE, '_pages')
if os.path.isdir(p):
    shutil.rmtree(p)
    print('removed _pages')
else:
    print('_pages 不存在')

# 2) 归档旧版 PDF
if not os.path.isdir(OLD):
    os.makedirs(OLD)

for f in sorted(os.listdir(BASE)):
    if not f.lower().endswith('.pdf'):
        continue
    if f.endswith('-v6.pdf'):
        continue
    src = os.path.join(BASE, f)
    dst = os.path.join(OLD, f)
    if os.path.exists(dst):
        print('已存在，跳过: %s' % f)
        continue
    try:
        shutil.move(src, dst)
        print('archived -> _旧版/%s' % f)
    except OSError as e:
        print('归档失败 %s : %s' % (f, e))

# 3) 终态
print('-' * 58)
for n in sorted(os.listdir(BASE)):
    q = os.path.join(BASE, n)
    if os.path.isdir(q):
        sz = sum(os.path.getsize(os.path.join(r, x)) for r, _, fs in os.walk(q) for x in fs)
        cnt = sum(len(fs) for _, _, fs in os.walk(q))
        print('[D] %-8s %7.1f MB  (%d files)' % (n, sz / 1048576, cnt))
    else:
        print('[F] %-8s %7.1f MB' % (n, os.path.getsize(q) / 1048576))
print('-' * 58)
o = sorted(os.listdir(OLD))
print('_旧版/ 内: %s' % o)
