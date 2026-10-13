# -*- coding: utf-8 -*-
"""P05 版式修正：把 c-split w64（图列 406.7px）改为「文本 : 图 = 1 : 1.22」，
图列加宽到 ~560px（4:3 图 → 高 420px），观感撑得住版面。

几何：内容宽 1060.8，gap 44 → 可用 1016.8
      1fr : 1.22fr（总 2.22）→ 文本 458.0 / 图 558.8
      4:3 图 → 高 419.1px  ✓
只改 grid-template-columns，文案与结构一字不动。
"""
import io, os, re

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
p = os.path.join(BASE, 'index.html')
s = io.open(p, encoding='utf-8').read()

OLD = '<div class="c-split w64" style="align-items:center">'
# 该 c-split 在 P05 里唯一（w64 只在 P05 用过），仍需核对次数
n = s.count(OLD)
print('c-split w64 occurrences:', n)
assert n == 1, 'expected exactly 1'

NEW = ('<div class="c-split" style="grid-template-columns:1fr 1.22fr;gap:44px;'
       'align-items:center;width:100%">')
s = s.replace(OLD, NEW)

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('[OK] P05 split ratio -> 1fr : 1.22fr  (图列 ~558.8px, 4:3 高 ~419px)')
