# -*- coding: utf-8 -*-
"""返工复算：各册「文化部分章节内的物料页」占比。
章节区间依据章节页位置推断（文化章节页 → 下一章节页之间）。"""
import re
from collections import Counter

PATH = r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260916-餐饮VI物料与场景应用盘点\01-工蜂产出\T2-标注-231页物料场景逐页索引.md"

BOOKS = ["三餐里", "小耕班", "摘山语", "蘑菇", "鸽子官"]
# (册, 文化章节起始页, 下一章节结束界限页) —— 依据 T2 明细中的「章节」页
# 三餐里 P08 文化部分 → P30 导视部分
# 小耕班 P07 文化部分 → P43 导视部分
# 摘山语 P11 文化部分 → P31 导视部分
# 蘑菇   P09 品牌文化 SCHEME → P42 品牌导视 SCHEME
# 鸽子官 P08 文化部分 → P50 物料部分
RANGES = {
    "三餐里": (8, 30),
    "小耕班": (7, 43),
    "摘山语": (11, 31),
    "蘑菇": (9, 42),
    "鸽子官": (8, 50),
}

rows = []
with open(PATH, encoding="utf-8") as f:
    for ln in f:
        s = ln.strip()
        if not s.startswith("|"):
            continue
        c = [x.strip() for x in s.strip("|").split("|")]
        if len(c) < 6:
            continue
        if not re.fullmatch(r"P\d{2}", c[1]) or c[0] not in BOOKS:
            continue
        rows.append((c[0], int(c[1][1:]), c[4], c[5]))

print("册      物料页B  其中文化章节内  占比")
lo, hi = 999.0, 0.0
for b in BOOKS:
    tot = sum(1 for r in rows if r[0] == b and r[2] == "B")
    a, z = RANGES[b]
    cul = sum(1 for r in rows if r[0] == b and r[2] == "B" and a < r[1] < z)
    pct = cul / tot * 100
    lo, hi = min(lo, pct), max(hi, pct)
    print(f"{b:6s} {tot:6d} {cul:12d}  {pct:.1f}%")
print(f"\n区间：{lo:.1f}% ~ {hi:.1f}%")
print("物料页总数核对：", sum(1 for r in rows if r[2] == "B"))
