# -*- coding: utf-8 -*-
"""裁掉 02-验收单.md 中残留的旧版 v2 章节（第 2 个「## 验收结论」起全部丢弃）。"""
import io, os

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '02-验收单.md')
s = io.open(p, encoding='utf-8').read()
lines = s.split('\n')
idx = [i for i, l in enumerate(lines) if l.startswith('## 验收结论')]
print('total lines       :', len(lines))
print('conclusion headers:', idx)

if len(idx) >= 2:
    cut = idx[1]
    # 向前吃掉紧邻的分隔线
    while cut > 0 and lines[cut - 1].strip() in ('', '---'):
        cut -= 1
    new = '\n'.join(lines[:cut]).rstrip() + '\n'
    io.open(p, 'w', encoding='utf-8', newline='\n').write(new)
    print('trimmed from line :', cut)
    print('new total lines   :', len(new.split('\n')))
else:
    print('no duplicate section, skip')
