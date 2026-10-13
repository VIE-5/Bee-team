# -*- coding: utf-8 -*-
"""整理产出目录：把回退用备份移入 _中间文件/_备份/，交付目录只留正式产物。"""
import os
import shutil

TASK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 任务根
OUT = os.path.join(TASK, '01-工蜂产出')
MID = os.path.join(TASK, '_中间文件')
BAKDIR = os.path.join(MID, '_备份')

os.makedirs(BAKDIR, exist_ok=True)

moves = [
    (os.path.join(OUT, 'index-v4-bak.html'), os.path.join(BAKDIR, 'index-v4-bak.html')),
    (os.path.join(OUT, 'assets', '_bak-v3'), os.path.join(BAKDIR, 'assets-bak-v3')),
]

for src, dst in moves:
    if not os.path.exists(src):
        print('[skip] 不存在:', os.path.basename(src))
        continue
    if os.path.exists(dst):
        print('[skip] 目标已存在:', dst)
        continue
    shutil.move(src, dst)
    print('[move]', os.path.basename(src), '->', os.path.relpath(dst, TASK))

print('-' * 58)
print('[交付目录 01-工蜂产出]')
for n in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, n)
    if os.path.isdir(p):
        sz = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(p) for f in fs)
        cnt = sum(len(fs) for _, _, fs in os.walk(p))
        print('  [D] %-22s %7.1f MB  (%d files)' % (n, sz / 1048576, cnt))
    else:
        print('  [F] %-22s %7.1f MB' % (n, os.path.getsize(p) / 1048576))
