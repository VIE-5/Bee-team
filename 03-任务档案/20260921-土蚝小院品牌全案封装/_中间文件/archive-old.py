# -*- coding: utf-8 -*-
"""把产出目录里的旧版 PDF 归档到 _旧版/（不删除）；被占用的跳过并报告。"""
import os
import shutil

TASK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(TASK, '01-工蜂产出')
OLD = os.path.join(OUT, '_旧版')

print('[_旧版 现有内容]')
for n in sorted(os.listdir(OLD)) if os.path.isdir(OLD) else []:
    p = os.path.join(OLD, n)
    print('  %.1f MB  %s' % (os.path.getsize(p) / 1048576, n))
print('-' * 58)

for ver in ('v2', 'v3', 'v4'):
    name = '土蚝小院-品牌视觉全案-%s.pdf' % ver
    src = os.path.join(OUT, name)
    dst = os.path.join(OLD, name)
    if not os.path.exists(src):
        print('[skip] 不存在:', name)
        continue
    try:
        shutil.move(src, dst)
        print('[move] %s -> _旧版/' % name)
    except OSError as e:
        print('[LOCK] %s 被占用，无法归档: %s' % (name, e))

print('-' * 58)
print('[交付目录终态]')
for n in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, n)
    if os.path.isdir(p):
        sz = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(p) for f in fs)
        print('  [D] %-22s %7.1f MB' % (n, sz / 1048576))
    else:
        print('  [F] %-22s %7.1f MB' % (n, os.path.getsize(p) / 1048576))
