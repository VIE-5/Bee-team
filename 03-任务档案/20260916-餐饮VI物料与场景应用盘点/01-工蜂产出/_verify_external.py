# -*- coding: utf-8 -*-
"""
T6 对撞报告 · 独立复算脚本 v2
=========================================
作用：不采信 T5A/T5B 工蜂自报的统计表，从「样本总表」原始行重新抽取 M/S 码并统计。
v2 修正：v1 的判定阈值把「百分数」与「比例」混用（9.4 >= 0.10 恒真），
         改为「零值判定有无 + ≥15% 判定强弱」，三源判定不再失真。
运行：python _verify_external.py
"""
import re
import os

BASE = os.path.dirname(os.path.abspath(__file__))


def read(name):
    with open(os.path.join(BASE, name), encoding='utf-8') as f:
        return f.read()


def parse_table(txt, section_start, section_end):
    seg = txt.split(section_start)[1].split(section_end)[0]
    rows = []
    for line in seg.split('\n'):
        s = line.strip()
        if not s.startswith('|'):
            continue
        if re.fullmatch(r'\|[\s:|-]+\|', s):
            continue
        rows.append(s)
    return rows[1:]


def cells_of(row):
    return [c.strip() for c in row.strip().strip('|').split('|')]


# ============================================================
# 一、T5A 外部案例样本
# ============================================================
ta = read('T5A-资料包-外部案例物料场景样本.md')
a_rows = parse_table(ta, '## 二、样本总表', '## 三、')

a_n = 0
a_M, a_S = {}, {}
a_m_items, a_s_items, a_declared_m, a_declared_s = 0, 0, 0, 0
a_biz, a_conf = {}, {}
a_rows_mismatch = []
a_recs = []  # 每行记录，供分组分析

for r in a_rows:
    c = cells_of(r)
    if len(c) < 11:
        print('[T5A] 列数异常，跳过:', len(c), r[:70])
        continue
    a_n += 1
    brand, biz, mcell, scell, conf = c[1], c[2], c[6], c[7], c[10]
    try:
        dec_m, dec_s = int(c[8]), int(c[9])
    except ValueError:
        dec_m = dec_s = None

    mcodes = {('M' + x) for x in re.findall(r'M(\d+)', mcell)}
    scodes = {('S' + x) for x in re.findall(r'S(\d+)', scell)}
    real_m = len([x for x in mcell.split(';') if x.strip()])
    real_s = len([x for x in scell.split(';') if x.strip()]) if scell not in ('—', '-', '') else 0

    for k in mcodes:
        a_M[k] = a_M.get(k, 0) + 1
    for k in scodes:
        a_S[k] = a_S.get(k, 0) + 1
    a_m_items += real_m
    a_s_items += real_s
    a_declared_m += dec_m or 0
    a_declared_s += dec_s or 0
    a_biz[biz] = a_biz.get(biz, 0) + 1
    a_conf[conf] = a_conf.get(conf, 0) + 1
    a_recs.append({'brand': brand, 'biz': biz, 'M': mcodes, 'S': scodes, 'conf': conf})

    if dec_m is not None and dec_m != real_m:
        a_rows_mismatch.append(('M', brand, dec_m, real_m))
    if dec_s is not None and dec_s != real_s:
        a_rows_mismatch.append(('S', brand, dec_s, real_s))

# ============================================================
# 二、T5B 商业套餐样本
# ============================================================
tb = read('T5B-资料包-外部商业交付口径与报价样本.md')
b_rows = parse_table(tb, '## 二、样本总表', '## 三、')

b_n = 0
b_M, b_S = {}, {}
b_plat, b_conf = {}, {}
b_items_known, b_items_sum = 0, 0

for r in b_rows:
    c = cells_of(r)
    if len(c) < 13:
        print('[T5B] 列数异常，跳过:', len(c), r[:70])
        continue
    b_n += 1
    plat, items, mcell, scell, conf = c[1], c[6], c[8], c[9], c[12]
    for k in {('M' + x) for x in re.findall(r'M(\d+)', mcell)}:
        b_M[k] = b_M.get(k, 0) + 1
    for k in {('S' + x) for x in re.findall(r'S(\d+)', scell)}:
        b_S[k] = b_S.get(k, 0) + 1
    b_plat[plat] = b_plat.get(plat, 0) + 1
    b_conf[conf] = b_conf.get(conf, 0) + 1
    if items.isdigit():
        b_items_sum += int(items)
        b_items_known += 1

# ============================================================
# 三、T5B 工蜂自报统计表（用于打假比对）
# ============================================================
TB_SELF_M = {'M1': 20, 'M2': 0, 'M3': 5, 'M4': 8, 'M5': 1, 'M6': 0, 'M7': 3, 'M8': 9,
             'M9': 9, 'M10': 10, 'M11': 5, 'M12': 0, 'M13': 11, 'M14': 0, 'M15': 0}

# ============================================================
# 四、我方 231 页实测基准
# ============================================================
MY_M = {'M1': 25, 'M2': 10, 'M3': 26, 'M4': 52, 'M5': 16, 'M6': 5, 'M7': 9, 'M8': 5,
        'M9': 23, 'M10': 0, 'M11': 0, 'M12': 0, 'M13': 0, 'M14': 0, 'M15': 0}
MY_S = {'S1': 3, 'S2': 5, 'S3': 7, 'S4': 1, 'S5': 1, 'S6': 1, 'S7': 1, 'S8': 0, 'S9': 0}
MY_B, MY_C = 171, 19

M_NAME = {'M1': '标识与辅助图形', 'M2': '章徽印记', 'M3': '匾额与墙面字', 'M4': '海报灯箱立牌',
          'M5': '卡片标签价格', 'M6': '旗帜吊挂', 'M7': '陈列展示', 'M8': '包装文创',
          'M9': '公示提示', 'M10': '办公事务用品', 'M11': '员工服装', 'M12': '车辆系统',
          'M13': '数字媒体', 'M14': '餐饮台面', 'M15': '会员促销印刷'}
S_NAME = {'S1': '门头与外立面', 'S2': '墙面部品', 'S3': '灯光与灯箱', 'S4': '门窗玻璃',
          'S5': '停车与外围导视', 'S6': '整店空间与室内效果', 'S7': '渠道与门店分布',
          'S8': '软装陈设', 'S9': '动线与导视系统'}
M_ORDER = ['M%d' % i for i in range(1, 16)]
S_ORDER = ['S%d' % i for i in range(1, 10)]

STRONG = 15.0  # 强弱阈值（百分数）


def verdict(my, ap, bp):
    has = [my > 0, ap > 0, bp > 0]
    n = sum(has)
    if n == 0:
        return '三源皆无'
    base = {1: '单源', 2: '双源', 3: '三源'}[n]
    tag = ''
    if n >= 2 and not has[0]:
        tag = '◆我缺口'
    elif has[0] and n < 3:
        tag = '★我有外弱'
    elif n == 3 and my >= STRONG and ap >= STRONG and bp >= STRONG:
        tag = '全强共振'
    elif n == 3:
        tag = '三源共振'
    return base + (' · ' + tag if tag else '')


# ============================================================
# 五、输出
# ============================================================
print('=' * 84)
print('【T5A 外部案例样本 · 独立复算】')
print('=' * 84)
print('案例数 N =', a_n)
print('物料条目总数 =', a_m_items, '｜ 工蜂自报合计 =', a_declared_m)
print('场景条目总数 =', a_s_items, '｜ 工蜂自报合计 =', a_declared_s)
print('业态分布 =', dict(sorted(a_biz.items(), key=lambda kv: -kv[1])))
print('可信度分布 =', a_conf)
print('自报项数 vs 实际条目数:', '全部一致 ✓' if not a_rows_mismatch else a_rows_mismatch)

print()
print('=' * 84)
print('【数据打假 · T5B 工蜂自报统计表 vs 我复算】')
print('=' * 84)
print('%-5s %-14s %10s %10s   %s' % ('码', '大类', '工蜂自报', '我复算', '判定'))
diffs = 0
for k in M_ORDER:
    sv, mv = TB_SELF_M[k], b_M.get(k, 0)
    ok = '一致' if sv == mv else '✗ 不一致'
    if sv != mv:
        diffs += 1
    print('%-5s %-14s %10d %10d   %s' % (k, M_NAME[k], sv, mv, ok))
print('→ T5B 自报表中 %d 处与原始行不符，以我复算值为准' % diffs)

print()
print('=' * 84)
print('【三源对撞表 · 核心产出】')
print('=' * 84)
print('实测=页次占比(171/19 基数) ｜ 案例=提及率(25) ｜ 套餐=覆盖率(20)')
print('口径不同 → 只比结构排序与有无，不比绝对值大小')
print()
print('%-5s %-14s %9s %9s %9s   %s' % ('码', '大类', '实测', '案例', '套餐', '三源判定'))
print('-' * 100)
print('--- 物料应用 ---')
for k in M_ORDER:
    my = MY_M[k] / MY_B * 100
    ap = a_M.get(k, 0) / a_n * 100
    bp = b_M.get(k, 0) / b_n * 100
    print('%-5s %-14s %8.1f%% %8.1f%% %8.1f%%   %s' % (k, M_NAME[k], my, ap, bp, verdict(my, ap, bp)))
print('--- 场景应用 ---')
for k in S_ORDER:
    my = MY_S[k] / MY_C * 100
    ap = a_S.get(k, 0) / a_n * 100
    bp = b_S.get(k, 0) / b_n * 100
    print('%-5s %-14s %8.1f%% %8.1f%% %8.1f%%   %s' % (k, S_NAME[k], my, ap, bp, verdict(my, ap, bp)))

print()
print('=' * 84)
print('【专项分析】')
print('=' * 84)
# 茶饮+烘焙 M8
tb_recs = [r for r in a_recs if r['biz'] in ('茶饮', '烘焙')]
tb_m8 = sum(1 for r in tb_recs if 'M8' in r['M'])
print('① 茶饮+烘焙样本 %d 例，含 M8 包装 %d 例 = %.1f%%' %
      (len(tb_recs), tb_m8, tb_m8 / len(tb_recs) * 100))
cy = [r for r in a_recs if r['biz'] == '茶饮']
bk = [r for r in a_recs if r['biz'] == '烘焙']
print('   茶饮 %d 例含 M8 %d 例 ｜ 烘焙 %d 例含 M8 %d 例' %
      (len(cy), sum(1 for r in cy if 'M8' in r['M']),
       len(bk), sum(1 for r in bk if 'M8' in r['M'])))

# 高可信度子集稳健性
hi = [r for r in a_recs if r['conf'] == '高']
hi_M8 = sum(1 for r in hi if 'M8' in r['M'])
hi_M1 = sum(1 for r in hi if 'M1' in r['M'])
print('② 高可信度子集 %d 例稳健性：M1 %d 例(%.0f%%) ｜ M8 %d 例(%.0f%%)' %
      (len(hi), hi_M1, hi_M1 / len(hi) * 100, hi_M8, hi_M8 / len(hi) * 100))

# M8 三源分歧
print('③ M8 包装三源分歧：实测 %.1f%% ｜ 案例 %.1f%% ｜ 套餐 %.1f%% → 极差 %.1f 个百分点' %
      (MY_M['M8'] / MY_B * 100, a_M.get('M8', 0) / a_n * 100, b_M.get('M8', 0) / b_n * 100,
       (a_M.get('M8', 0) / a_n * 100) - (MY_M['M8'] / MY_B * 100)))

# 六缺口
print('④ 六缺口类（M10-M15）三源覆盖：')
for k in ['M10', 'M11', 'M12', 'M13', 'M14', 'M15']:
    print('   %s %-12s 实测 %2d 页次 ｜ 案例 %2d/25 ｜ 套餐 %2d/20' %
          (k, M_NAME[k], MY_M[k], a_M.get(k, 0), b_M.get(k, 0)))

# 我方独有
print('⑤ 我方独有项（实测 >0 且外部双源均低）：')
for k in M_ORDER + S_ORDER:
    if k.startswith('M'):
        my, ap, bp = MY_M[k] / MY_B * 100, a_M.get(k, 0) / a_n * 100, b_M.get(k, 0) / b_n * 100
    else:
        my, ap, bp = MY_S[k] / MY_C * 100, a_S.get(k, 0) / a_n * 100, b_S.get(k, 0) / b_n * 100
    if my > 0 and (ap < STRONG or bp < STRONG):
        nm = M_NAME[k] if k.startswith('M') else S_NAME[k]
        print('   %s %-12s 实测 %.1f%% ｜ 案例 %.1f%% ｜ 套餐 %.1f%%' % (k, nm, my, ap, bp))

print()
print('【T5B 价格/项数】')
print('明确项数样本 %d 个 ｜ 项数合计 %d ｜ 均值 %.1f' %
      (b_items_known, b_items_sum, b_items_sum / b_items_known if b_items_known else 0))
print('平台分布 =', dict(sorted(b_plat.items(), key=lambda kv: -kv[1])))
print()
print('复算完毕。')
