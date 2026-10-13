# -*- coding: utf-8 -*-
"""
unify-tracking.py —— 把 HTML 里行内硬编码的 letter-spacing 统一到刻度变量。

映射（按视觉档位，非按原数值机械替换）：
  .05em / .06em / .08em  →  var(--ls-base)   中文小标签 / 卡片标题
  .10em / .14em / .16em  →  var(--ls-wide)   中文标题 / 强调小字 / 竖排边注
  .20em / .22em / .24em  →  var(--ls-wide)   长字距小字（统一收到 wide 档）
  .28em / .30em          →  var(--ls-en)     英文大写小标

⚠️ 只改 letter-spacing 的值，不动其它属性。
⚠️ 收尾双向复核：改后不应再存在 `letter-spacing:.NNem` 字面量。
"""
import re
import sys
from pathlib import Path

MAP = {
    ".05em": "var(--ls-base)",
    ".06em": "var(--ls-base)",
    ".08em": "var(--ls-base)",
    ".10em": "var(--ls-wide)",
    ".12em": "var(--ls-wide)",
    ".14em": "var(--ls-wide)",
    ".16em": "var(--ls-wide)",
    ".20em": "var(--ls-wide)",
    ".22em": "var(--ls-wide)",
    ".24em": "var(--ls-wide)",
    ".28em": "var(--ls-en)",
    ".30em": "var(--ls-en)",
}

p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
before = len(re.findall(r"letter-spacing:\s*\.[0-9]+em", s))

for k, v in MAP.items():
    s = s.replace(f"letter-spacing:{k}", f"letter-spacing:{v}")
    s = s.replace(f"letter-spacing: {k}", f"letter-spacing:{v}")

p.write_text(s, encoding="utf-8")

after = re.findall(r"letter-spacing:\s*\.[0-9]+em", s)
print(f"替换前字面量 {before} 处（共 {len(MAP)} 种档位映射）")
print(f"替换后残留字面量 {len(after)} 处")
if after:
    print("  [!] 仍有未映射的值：", sorted(set(after)))
else:
    print("  [OK] 全部字距已走刻度变量")
