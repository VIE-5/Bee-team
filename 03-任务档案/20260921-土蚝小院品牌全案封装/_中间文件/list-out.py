# -*- coding: utf-8 -*-
"""产出目录终态核对。"""
import os

BASE = r'D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260921-土蚝小院品牌全案封装\01-工蜂产出'
print('exists:', os.path.isdir(BASE))
print('-' * 56)
for n in sorted(os.listdir(BASE)):
    p = os.path.join(BASE, n)
    if os.path.isdir(p):
        sz = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(p) for f in fs)
        cnt = sum(len(fs) for _, _, fs in os.walk(p))
        print('[D] %-16s %7.1f MB  (%d files)' % (n, sz / 1048576, cnt))
    else:
        print('[F] %-16s %7.1f MB' % (n, os.path.getsize(p) / 1048576))
