# -*- coding: utf-8 -*-
"""
由母版 build.py 生成某单的「实例脚本」
=================================================================
用法：改下面【配置区】的 MASTER / TARGET / REPL 三条，然后
    python gen_instance.py

为什么要这么做：母版是**唯一维护点**。各单的 build_xxx.py 都是它的派生物，
母版改了（加版式、修几何），重新生成一遍即全部同步 —— 不会出现"五个单五套代码"。

REPL 的「查找串」必须与母版里的字面**完全一致**（含空格，但不含行尾注释之后的追加）。
任何一条匹配不上会**直接报错退出**，不会静默生成半成品 —— 这是刻意的。
=================================================================
"""
import io

# ==================== 配置区 ====================
MASTER = r'D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\04-知识沉淀\母版\Logo-Scheme-Show-Master\build.py'
TARGET = r'D:\...\<某单目录>\_work\build_show.py'

# (母版中的查找串, 本单要替换成的串)
REPL = [
    # ① 工作目录
    ("WK = r'D:\\...\\_work'",
     "WK = r'D:\\WORK——Vie\\贵州遵义\\碗香\\Logo二-全案封装\\_work'"),
    # ② 交付路径
    ("OUT = r'D:\\...\\01-工蜂产出\\标志方案展示.pptx'",
     "OUT = r'D:\\WORK——Vie\\贵州遵义\\碗香\\Logo二-全案封装\\01-工蜂产出\\碗香-标志方案展示.pptx'"),
    # ③ 品牌字 / 强调色（若与母版默认不同才需要）
    # ("BRAND_NAME = '碗香'", "BRAND_NAME = '某某'"),
    # ④ 页型文案（本单专属措辞）
    ("LEAD_P4_TITLE = '同一形象骨架 · 三套色彩方案'",
     "LEAD_P4_TITLE = '同一厨师形象 · 三套色彩方案'"),
    ("LEAD_P4 = '三版共用同一形象与牌匾骨架，靠配色与顶标用字区分使用场合'",
     "LEAD_P4 = '三版共用同一人物与牌匾骨架，靠配色与顶标用字区分使用场合'"),
]
DOCSTRING_FROM = '标志方案展示 · 通用版式构建（母版 · 5 页）'
DOCSTRING_TO = '碗香 · 标志方案展示（二）实例｜由母版 Logo-Scheme-Show-Master 生成'
# ================================================

s = io.open(MASTER, encoding='utf-8').read()
for a, b in REPL:
    if a not in s:
        raise SystemExit('!! 母版中未找到待替换片段（母版可能已改动）: ' + a[:56])
    s = s.replace(a, b)

if DOCSTRING_FROM in s:
    s = s.replace(DOCSTRING_FROM, DOCSTRING_TO)

io.open(TARGET, 'w', encoding='utf-8').write(s)
print('generated ->', TARGET, len(s), 'chars')
