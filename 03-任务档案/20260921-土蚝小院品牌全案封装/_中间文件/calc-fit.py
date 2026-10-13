# -*- coding: utf-8 -*-
"""按新素材比例，计算四页图片的合理限高。
画布 1360x850，--mx:11% (149.6px)，--hdr:15% (127.5px)。
"""
CANVAS_W, CANVAS_H = 1360, 850
MX = 149.6
HDR = 127.5
FOOT = 0.09 * CANVAS_H   # 页脚区约 9%
CW = CANVAS_W - 2 * MX   # 1060.8 内容宽

print('canvas %dx%d, mx=%.1f, cw=%.1f, hdr=%.1f, foot=%.1f' % (CANVAS_W, CANVAS_H, MX, CW, HDR, FOOT))
print('=' * 70)

# P05: c-split w64 -> 文本列 : 图列 = 64 : 36 ? 实际 w64 表示图列占比
# 查 theme.css 的 c-split 定义
import io, os, re
base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出', 'assets')
css = io.open(os.path.join(base, 'theme.css'), encoding='utf-8').read()
for m in re.finditer(r'\.c-split[^{]*\{[^}]*\}', css):
    print(m.group(0).replace('\n', ' ')[:300])
print('-' * 70)
for m in re.finditer(r'\.c-split\.w\d+[^{]*\{[^}]*\}', css):
    print(m.group(0).replace('\n', ' ')[:300])
print('-' * 70)
for m in re.finditer(r'\.bd[^{]*\{[^}]*\}', css):
    print(m.group(0).replace('\n', ' ')[:300])
