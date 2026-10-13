# -*- coding: utf-8 -*-
"""核算 T2 索引表的分类统计，验证手写汇总是否自洽。"""
import re, sys, os
from collections import Counter, defaultdict

PATH = r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260916-餐饮VI物料与场景应用盘点\01-工蜂产出\T2-标注-231页物料场景逐页索引.md"

BOOKS = ["三餐里", "小耕班", "摘山语", "蘑菇", "鸽子官"]

with open(PATH, encoding="utf-8") as f:
    lines = f.readlines()

rows = []
for ln in lines:
    s = ln.strip()
    if not s.startswith("|"):
        continue
    cells = [c.strip() for c in s.strip("|").split("|")]
    if len(cells) < 6:
        continue
    book, page, cat, detail = cells[0], cells[1], cells[4], cells[5]
    if not re.fullmatch(r"P\d{2}", page):
        continue
    if book not in BOOKS:
        continue
    rows.append((book, page, cat, detail))

print("解析到明细行总数：", len(rows))

# 去重校验
seen = set()
dup = []
for book, page, cat, detail in rows:
    k = (book, page)
    if k in seen:
        dup.append(k)
    seen.add(k)
print("重复行：", dup if dup else "无")

per_book = Counter(b for b, _, _, _ in rows)
print("\n各册页数：")
for b in BOOKS:
    print(f"  {b:6s} {per_book[b]:3d}")
print("  合计  ", sum(per_book.values()))

# 三大类
cat_cnt = defaultdict(Counter)
for book, page, cat, detail in rows:
    cat_cnt[book][cat] += 1

all_cats = ["A", "B", "C"]
print("\n三大类分布：")
print("册      总  A  B  C")
tot = Counter()
for b in BOOKS:
    t = per_book[b]
    a, bb, c = cat_cnt[b]["A"], cat_cnt[b]["B"], cat_cnt[b]["C"]
    tot["A"] += a; tot["B"] += bb; tot["C"] += c; tot["T"] += t
    print(f"{b:6s} {t:3d} {a:3d} {bb:3d} {c:3d}")
print(f"合计   {tot['T']:3d} {tot['A']:3d} {tot['B']:3d} {tot['C']:3d}")

for k, name in [("A", "品牌基座"), ("B", "物料应用"), ("C", "场景应用")]:
    print(f"  {name}: {tot[k]}  占比 {tot[k]/tot['T']*100:.1f}%")

# 细类
mat = defaultdict(Counter)
scn = defaultdict(Counter)
for book, page, cat, detail in rows:
    if cat == "B" and re.fullmatch(r"M\d", detail):
        mat[detail][book] += 1
    if cat == "C" and re.fullmatch(r"S\d", detail):
        scn[detail][book] += 1

print("\n物料细类（M）：")
print("码   三餐里 小耕班 摘山语 蘑菇 鸽子官  合计  覆盖册")
mkeys = sorted(mat.keys())
mtot = Counter()
for k in mkeys:
    row = [mat[k][b] for b in BOOKS]
    s = sum(row)
    mtot[k] = s
    cover = sum(1 for x in row if x > 0)
    print(f"{k:4s} {row[0]:5d} {row[1]:6d} {row[2]:6d} {row[3]:4d} {row[4]:6d}  {s:4d}   {cover}/5")
print("M 合计：", sum(mtot.values()))

print("\n场景细类（S）：")
stot = Counter()
for k in sorted(scn.keys()):
    row = [scn[k][b] for b in BOOKS]
    s = sum(row)
    stot[k] = s
    print(f"{k:4s} {row}  合计 {s}")
print("S 合计：", sum(stot.values()))

print("\n校验：B 应为 171 →", sum(mtot.values()), "| C 应为 19 →", sum(stot.values()))

# 未归类检查
un = [(b, p, c, d) for b, p, c, d in rows if (c == "B" and not re.fullmatch(r"M\d", d)) or (c == "C" and not re.fullmatch(r"S\d", d))]
print("细类标注异常行：", un if un else "无")
