# -*- coding: utf-8 -*-
r"""
W4 守卫蜂 · 独立复算脚本（对抗性验收，不依赖 T3 的任何中间结果）
从 T2 逐页明细重新统计，逐项比对 T3 报告数字；并校验页码完整性 / 文化章节占比 / 页码证据抽查。
运行：C:/Users/27612/.workbuddy/binaries/python/versions/3.13.12/python.exe _guard_recheck.py
"""
import re, os
from collections import Counter, defaultdict

BASE = r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260916-餐饮VI物料与场景应用盘点\01-工蜂产出"
T2 = os.path.join(BASE, "T2-标注-231页物料场景逐页索引.md")

# 数据行里 册 字段用的简称
BOOKS = ["三餐里", "小耕班", "摘山语", "蘑菇", "鸽子官"]
BOOK_DISPLAY = {"三餐里": "三餐里", "小耕班": "小耕班", "摘山语": "摘山语",
                "蘑菇": "蘑菇围炉", "鸽子官": "鸽子官"}
EXPECT_TOTAL = {"三餐里": 35, "小耕班": 51, "摘山语": 37, "蘑菇": 49, "鸽子官": 59}

with open(T2, encoding="utf-8") as f:
    lines = f.readlines()

rows = []
for ln in lines:
    s = ln.strip()
    if not s.startswith("|"):
        continue
    cells = [c.strip() for c in s.strip("|").split("|")]
    if len(cells) < 6:
        continue
    book, page, header, detail, cat, sub = cells[0], cells[1], cells[2], cells[3], cells[4], cells[5]
    if not re.fullmatch(r"P\d{2}", page):
        continue
    if book not in BOOKS:
        continue
    rows.append({"book": book, "page": page, "header": header,
                 "detail": detail, "cat": cat, "sub": sub})

print("=" * 70)
print("解析到明细行总数：", len(rows), "（预期 231）")
assert len(rows) == 231, "明细行数不等于 231！"

# ---------- 1. 页码完整性（无跳号 / 无重复） ----------
print("\n[完整性] 各册页号连续性 / 重复校验")
ok_complete = True
for b in BOOKS:
    ps = sorted(int(r["page"][1:]) for r in rows if r["book"] == b)
    expect = list(range(1, EXPECT_TOTAL[b] + 1))
    dups = [p for p in set(ps) if ps.count(p) > 1]
    missing = [p for p in expect if p not in ps]
    extra = [p for p in ps if p > EXPECT_TOTAL[b]]
    flag = "OK" if (not dups and not missing and not extra and len(ps) == EXPECT_TOTAL[b]) else "FAIL"
    if flag != "OK":
        ok_complete = False
    print(f"  {BOOK_DISPLAY[b]:6s} 实际 {len(ps):3d} 预期 {EXPECT_TOTAL[b]:3d} "
          f"重复 {dups or '无'} 缺号 {missing or '无'} 超界 {extra or '无'} -> {flag}")
print("  完整性总判定:", "OK" if ok_complete else "FAIL")

# ---------- 2. A/B/C 三大类 ----------
print("\n[复算 1] 三大类 A/B/C")
cat_book = defaultdict(Counter)
for r in rows:
    cat_book[r["book"]][r["cat"]] += 1
tot = Counter()
abctab = {}
for b in BOOKS:
    a, bb, c = cat_book[b]["A"], cat_book[b]["B"], cat_book[b]["C"]
    tot["A"] += a; tot["B"] += bb; tot["C"] += c; tot["T"] += a + bb + c
    abctab[b] = (a, bb, c)
for b in BOOKS:
    a, bb, c = abctab[b]
    print(f"  {BOOK_DISPLAY[b]:6s} 总 {a+bb+c:3d}  A {a:2d}  B {bb:2d}  C {c:2d}")

# T3 报告值（取自 T3 §1.3）
T3_ABC = {
    "三餐里": (6, 24, 5), "小耕班": (9, 38, 4), "摘山语": (8, 27, 2),
    "蘑菇": (8, 40, 1), "鸽子官": (10, 42, 7),
}
T3_TOT = (41, 171, 19)
def cmp(label, got, exp):
    ok = got == exp
    print(f"    {label}: 复算 {got} | T3 {exp} -> {'一致' if ok else '**不一致**'}")
    return ok

print("  -- A/B/C 逐项比对 T3 --")
all_ok = True
for b in BOOKS:
    g = abctab[b]; e = T3_ABC[b]
    all_ok &= cmp(f"{BOOK_DISPLAY[b]} A/B/C", g, e)
all_ok &= cmp("合计 A/B/C", (tot["A"], tot["B"], tot["C"]), T3_TOT)
# 占比
for name, k in [("A 占比", "A"), ("B 占比", "B"), ("C 占比", "C")]:
    g = round(tot[k] / tot["T"] * 100, 1)
    exp_map = {"A": 17.7, "B": 74.0, "C": 8.2}
    ok = abs(g - exp_map[k]) < 0.05
    all_ok &= ok
    print(f"    {name}: 复算 {g}% | T3 {exp_map[k]}% -> {'一致' if ok else '**不一致**'}")

# ---------- 3. M1-M9 物料细类 ----------
print("\n[复算 2] 物料细类 M1-M9（分册 + 合计 + 占B + 覆盖册）")
mat_book = defaultdict(Counter)
for r in rows:
    if r["cat"] == "B" and re.fullmatch(r"M\d", r["sub"]):
        mat_book[r["sub"]][r["book"]] += 1
MKEYS = [f"M{i}" for i in range(1, 10)]
# T3 报告值（§二）
T3_M = {
    "M1": [3, 3, 6, 5, 8, 25, 14.6, "5/5"],
    "M2": [1, 1, 4, 0, 4, 10, 5.8, "4/5"],
    "M3": [3, 4, 5, 3, 11, 26, 15.2, "5/5"],
    "M4": [8, 13, 4, 21, 6, 52, 30.4, "5/5"],
    "M5": [1, 3, 1, 5, 6, 16, 9.4, "5/5"],
    "M6": [0, 2, 1, 1, 1, 5, 2.9, "4/5"],
    "M7": [0, 6, 3, 0, 0, 9, 5.3, "2/5"],
    "M8": [0, 0, 0, 2, 3, 5, 2.9, "2/5"],
    "M9": [8, 6, 3, 3, 3, 23, 13.5, "5/5"],
}
print("  码   三餐里 小耕班 摘山语 蘑菇 鸽子官  合计  占B%  覆盖册  | 比对")
for k in MKEYS:
    row = [mat_book[k][b] for b in BOOKS]
    s = sum(row); cover = sum(1 for x in row if x > 0)
    pct = round(s / tot["B"] * 100, 1) if tot["B"] else 0
    exp = T3_M[k]
    ok = (row == exp[:5] and s == exp[5] and abs(pct - exp[6]) < 0.05 and f"{cover}/5" == exp[7])
    all_ok &= ok
    print(f"  {k:4s} {row[0]:5d} {row[1]:6d} {row[2]:6d} {row[3]:4d} {row[4]:6d}  {s:4d}  {pct:4.1f}%  {cover}/5 "
          f"| T3合计{exp[5]} 占B{exp[6]}% 覆盖{exp[7]} -> {'一致' if ok else '**不一致**'}")
mtot = sum(mat_book[k][b] for k in MKEYS for b in BOOKS)
print(f"  M 合计复算 {mtot} | T3 171 -> {'一致' if mtot == 171 else '**不一致**'}")
all_ok &= (mtot == 171)

# ---------- 4. S1-S7 场景细类 ----------
print("\n[复算 3] 场景细类 S1-S7（合计 + 占C）")
scn_book = defaultdict(Counter)
for r in rows:
    if r["cat"] == "C" and re.fullmatch(r"S\d", r["sub"]):
        scn_book[r["sub"]][r["book"]] += 1
SKEYS = [f"S{i}" for i in range(1, 8)]
T3_S = {"S1": 3, "S2": 5, "S3": 7, "S4": 1, "S5": 1, "S6": 1, "S7": 1}
print("  码   各册计数(简)        合计  占C%  | 比对")
for k in SKEYS:
    row = [scn_book[k][b] for b in BOOKS]
    s = sum(row); pct = round(s / tot["C"] * 100, 1) if tot["C"] else 0
    exp = T3_S[k]; exp_pct = round(exp / 19 * 100, 1)
    ok = (s == exp and abs(pct - exp_pct) < 0.05)
    all_ok &= ok
    print(f"  {k:4s} {str(row):18s} {s:4d}  {pct:4.1f}% | T3 {exp} 占C{exp_pct}% -> {'一致' if ok else '**不一致**'}")
stot = sum(scn_book[k][b] for k in SKEYS for b in BOOKS)
print(f"  S 合计复算 {stot} | T3 19 -> {'一致' if stot == 19 else '**不一致**'}")
all_ok &= (stot == 19)

# ---------- 5. 细类标注异常（B 无 M / C 无 S） ----------
un = [(r["book"], r["page"], r["cat"], r["sub"]) for r in rows
      if (r["cat"] == "B" and not re.fullmatch(r"M\d", r["sub"]))
      or (r["cat"] == "C" and not re.fullmatch(r"S\d", r["sub"]))]
print("\n[校验] 细类标注异常行（B 应带 M、C 应带 S）：", un if un else "无")

# ---------- 6. 文化章节占比（逻辑自洽性重点） ----------
print("\n[复算 4] 物料页挂在「品牌文化」章节的比例（验证 T3 结论#5）")
# 方法A：页眉栏目精确等于「品牌文化」的 B 页
# 方法B：落在「文化部分」章节区间内（下一个章节标记之前）的 B 页
def chapter_b_book(book):
    br = [r for r in rows if r["book"] == book]
    # 找文化部分起点页
    cul_start = None
    next_start = None
    for r in br:
        if "文化部分" in r["detail"]:
            cul_start = int(r["page"][1:])
            break
    if cul_start is None:
        return None, None
    for r in br:
        p = int(r["page"][1:])
        if p > cul_start and ("部分" in r["detail"] or "BASE" in r["detail"]) and next_start is None:
            # 下一个章节标记（基础/空间/物料/导视部分）
            if any(x in r["detail"] for x in ["基础部分", "空间部分", "物料部分", "导视部分"]):
                next_start = p
    if next_start is None:
        next_start = EXPECT_TOTAL[book] + 1
    b_in_cul = [r for r in br if r["cat"] == "B" and cul_start < int(r["page"][1:]) < next_start]
    b_exact = [r for r in br if r["cat"] == "B" and r["header"] == "品牌文化"]
    return len(b_in_cul), len(b_exact)

print("  册       文化部分区间B  品牌文化页眉B  总B   区间占比   页眉占比")
frac_range = []
for b in BOOKS:
    cin, cex = chapter_b_book(b)
    tb = cat_book[b]["B"]
    if cin is not None:
        fr = cin / tb * 100
        fe = cex / tb * 100
        frac_range.append(fr)
        print(f"  {BOOK_DISPLAY[b]:6s}  {cin:3d}           {cex:3d}          {tb:2d}   {fr:5.1f}%    {fe:5.1f}%")
print(f"  文化部分区间占比范围：{min(frac_range):.1f}% ~ {max(frac_range):.1f}%")
print("  >> T3 结论#5 称『各册占比 79%~92%』—— 实际区间如上，需比对。")

# ---------- 7. 页码证据抽查（T3 引用于 T2 是否真实） ----------
print("\n[复算 5] T3 页码证据抽查（(册,页) -> T2 实标归类/细类）")
lookup = {(r["book"], r["page"]): (r["cat"], r["sub"], r["detail"]) for r in rows}
# (册简称, 页, T3 中声称的类别, 期望细类或 None, 备注)
spot = [
    ("三餐里", "P15", "B", "M4", "竖版海报"),
    ("三餐里", "P16", "B", "M4", "竖版海报"),
    ("三餐里", "P17", "B", "M4", "竖版海报"),
    ("小耕班", "P18", "B", "M4", "竖版海报"),
    ("小耕班", "P22", "B", "M4", "竖版海报"),
    ("蘑菇", "P21", "B", "M4", "竖版海报"),
    ("蘑菇", "P29", "B", "M4", "竖版海报"),
    ("鸽子官", "P45", "B", "M4", "外卖打包广告牌"),
    ("三餐里", "P10", "B", "M2", "T3 列入 M3 匾额，需查 T2"),  # 重点
    ("鸽子官", "P15", "C", "S2", "T3 列入 M3，需查 T2"),         # 重点
    ("鸽子官", "P16", "C", "S2", "T3 列入 M3，需查 T2"),         # 重点
    ("鸽子官", "P17", "C", "S2", "T3 列入 M3，需查 T2"),         # 重点
    ("三餐里", "P34", "B", "M9", "温馨提示(8枚)"),
    ("摘山语", "P34", "B", "M9", "温馨提示(4枚)"),
    ("蘑菇", "P47", "B", "M9", "温馨提示(4枚)"),
    ("三餐里", "P10", "B", "M2", "圆章(4枚)"),
    ("鸽子官", "P11", "B", "M2", "圆章(5枚)"),
    ("鸽子官", "P22", "B", "M5", "菜单牌(6枚)"),
    ("鸽子官", "P56", "B", "M8", "打包袋"),
    ("蘑菇", "P45", "B", "M6", "钱庄吊挂牌"),
    ("蘑菇", "P43", "C", "S1", "门头"),
    ("鸽子官", "P57", "C", "S7", "门店分布"),
    ("摘山语", "P25", "B", "M7", "文化墙"),
]
mismatch_evidence = []
for b, p, exp_cat, exp_sub, note in spot:
    key = (b, p)
    if key not in lookup:
        print(f"  **缺失** {b} {p} 在 T2 中不存在！（{note}）")
        mismatch_evidence.append((b, p, "不存在", note))
        continue
    cat, sub, detail = lookup[key]
    ok = (cat == exp_cat and (exp_sub is None or sub == exp_sub))
    mark = "吻合" if ok else "**不符**"
    if not ok:
        mismatch_evidence.append((b, p, f"T2={cat}{sub}", note))
    print(f"  {b} {p}: T2={cat}{sub} | 期望 {exp_cat}{exp_sub or ''} -> {mark}  ({note})")
print(f"\n  证据抽查不符项：{len(mismatch_evidence)}")
for m in mismatch_evidence:
    print("    -", m)

print("\n" + "=" * 70)
print("总判定：所有统计项逐项比对", "全部一致 ✅" if all_ok else "**存在不一致 ❌**")
print("=" * 70)
