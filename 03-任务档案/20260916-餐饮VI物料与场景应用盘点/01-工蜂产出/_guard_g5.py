# -*- coding: utf-8 -*-
"""
_guard_g5.py · W4 守卫蜂 第三轮独立复算脚本
纯从 T6 正则/分列抽取三源数值，与 T8 主表 + _gen_checklist.py 的 CODE 字典逐格比对。
"""
import re, os, importlib.util

BASE = r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260916-餐饮VI物料与场景应用盘点\01-工蜂产出"
T6 = os.path.join(BASE, "T6-报告-外部样本与实测样本对撞.md")
T8 = os.path.join(BASE, "T8-清单-餐饮品牌VI全案物料与场景完整清单.md")
GEN = os.path.join(BASE, "_gen_checklist.py")

def pct(x):
    x = x.replace("*", "").replace("%", "").replace(" ", "")
    if x in ("", "—", "-"):
        return None
    return float(x)

def code_of(cell):
    m = re.search(r"([MS]\d+)", cell)
    return m.group(1) if m else None

# ---------- A. T6 §2.1 / §2.2 ----------
t6 = open(T6, encoding="utf-8").read()
i1, j1 = t6.find("### 2.1"), t6.find("### 2.2")
i2, j2 = t6.find("### 2.2"), t6.find("### 2.3")
expected, expected_raw = {}, {}
for seg in (t6[i1:j1], t6[i2:j2]):
    for line in seg.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        # 期望形状: ['', code, 大类, a, b, c, 判定, '']
        if len(cells) < 7:
            continue
        c = code_of(cells[1])
        if not c:
            continue
        a, b, cc = pct(cells[3]), pct(cells[4]), pct(cells[5])
        if a is None or b is None or cc is None:
            continue
        expected[c] = (a, b, cc)
        expected_raw[c] = (cells[3], cells[4], cells[5])

print("=" * 72)
print("A. T6 抽取三源码（共 %d 个）" % len(expected))
print("=" * 72)
for k in sorted(expected):
    print("  %-4s  %8s %8s %8s" % (k, expected_raw[k][0], expected_raw[k][1], expected_raw[k][2]))

# ---------- B. T8 主表带码行 ----------
t8 = open(T8, encoding="utf-8").read()
t8_rows = []
for line in t8.splitlines():
    if not line.strip().startswith("|"):
        continue
    cells = [c.strip() for c in line.split("|")]
    # 主表行形状: ['', idx, 物料项, 码, 规格, 实测, 案例, 套餐, 判定, 动作, '']
    if len(cells) < 10:
        continue
    c = code_of(cells[3])
    if not c:
        continue
    a, b, cc = pct(cells[5]), pct(cells[6]), pct(cells[7])
    if a is None or b is None or cc is None:
        continue
    t8_rows.append((cells[1], cells[2], c, a, b, cc, cells[8], cells[9]))

print("")
print("=" * 72)
print("B. T8 主表带码行（共 %d 行） vs T6" % len(t8_rows))
print("=" * 72)
mismatch = []
for idx, name, c, a, b, cc, verdict, act in t8_rows:
    if c not in expected:
        mismatch.append((idx, c, "T6无码", None)); continue
    if (a, b, cc) != expected[c]:
        mismatch.append((idx, c, (a, b, cc), expected[c]))

print("-- B 结果 --")
if not mismatch:
    print("  [OK] 全部 %d 行三源数值与 T6 逐格一致（0%%/0.0%% 已归一）" % len(t8_rows))
else:
    print("  [FAIL] %d 处不一致：" % len(mismatch))
    for idx, c, got, exp in mismatch:
        print("    %s %s : T8=%s  T6=%s" % (idx, c, got, exp))
print("  格式留痕：T6 写 '0%%'（M2/S5/S7 等），T8 写 '0.0%%'，数值等价。")

# 每码一致性（T8 内同码行应同值）
percode = {}
for idx, name, c, a, b, cc, v, act in t8_rows:
    percode.setdefault(c, set()).add((a, b, cc))
intra = {k: v for k, v in percode.items() if len(v) > 1}
print("  T8 同码多值冲突：%s" % (["%s:%s" % (k, intra[k]) for k in intra] or "无"))

# ---------- C. CODE 字典 ----------
print("")
print("=" * 72)
print("C. _gen_checklist.py CODE 字典 vs T6")
print("=" * 72)
spec = importlib.util.spec_from_file_location("genmod", GEN)
genmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(genmod)
CODE = genmod.CODE
code_mismatch = []
for k, v in CODE.items():
    if k not in expected:
        code_mismatch.append((k, "T6无码", None)); continue
    if (v["a"], v["b"], v["c"]) != expected[k]:
        code_mismatch.append((k, (v["a"], v["b"], v["c"]), expected[k]))
if not code_mismatch:
    print("  [OK] CODE 字典 %d 个码三源数值与 T6 逐格一致" % len(CODE))
else:
    print("  [FAIL] %d 处不一致：" % len(code_mismatch))
    for it in code_mismatch:
        print("    ", it)

# ---------- D. 87 项结构 ----------
print("")
print("=" * 72)
print("D. 88 项结构自洽（返工补 1 项「火柴盒」后）")
print("=" * 72)
material = sum(1 for r in t8_rows if r[2].startswith("M"))
scene = sum(1 for r in t8_rows if r[2].startswith("S"))
base_bare = len(re.findall(r"^\|\s*〇-\d+\s*\|(.+?)\|\s*—\s*\|", t8, re.M))
print("  物料=%d 场景=%d 基座裸项=%d 合计=%d" % (material, scene, base_bare, material+scene+base_bare))
ok_d = (material == 71 and scene == 9 and base_bare == 8 and material+scene+base_bare == 88)
print("  T8 自述 88=基座8+物料71+场景9 -> %s" % ("[OK] 自洽" if ok_d else "[FAIL]"))

# ---------- E. §六 行业数据 ----------
print("")
print("=" * 72)
print("E. T8 §六 行业数据 vs T5C 关键数值")
print("=" * 72)
for n in ["57,982", "747", "339", "25%", "54%", "14,191", "17,469", "6.3", "1,286.3", "440.1", "84%"]:
    print("  %-10s %s" % (n, "[OK]" if n in t8 else "[FAIL] 缺失"))
print("  84%% 海外限定保留：%s" % ("[OK]" if ("海外" in t8 and "不可外推" in t8) else "[FAIL]"))

# ---------- 汇总 ----------
print("")
print("=" * 72)
print("汇总")
print("=" * 72)
print("  T6 抽取码数        :", len(expected))
print("  T8 主表带码行数     :", len(t8_rows))
print("  T8 主表数值不一致数 :", len(mismatch))
print("  T8 同码多值冲突     :", len(intra))
print("  CODE 字典不一致数   :", len(code_mismatch))
print("  88 项结构           :", "自洽" if ok_d else "异常")
print("=" * 72)
