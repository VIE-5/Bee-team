# -*- coding: utf-8 -*-
"""
W4 守卫蜂 · G4 出厂验收 · 独立复算脚本
========================================
独立于蜂王 _verify_external.py，从 T5A/T5B 样本总表「原始行」重新抽取 M/S 码，
统计提及率/覆盖率，并与 T6 报告 §2.1/§2.2 对撞表、§三 数据打假记录逐格比对。

实测基准（①我方 231 页）按任务要求作为既有资产，不重验，直接采用 T3 已发布数字。
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
# 一、T5A 外部案例样本（原始行重抽）
# ============================================================
ta = read('T5A-资料包-外部案例物料场景样本.md')
a_rows = parse_table(ta, '## 二、样本总表', '## 三、')

a_n = 0
a_M, a_S = {}, {}
a_declared_m_sum = 0
a_real_m_sum = 0
a_biz = {}
for r in a_rows:
    c = cells_of(r)
    if len(c) < 11:
        print('[T5A] 列数异常跳过:', len(c), r[:60]); continue
    a_n += 1
    biz, mcell, scell = c[2], c[6], c[7]
    dec_m = int(c[8]) if c[8].isdigit() else None
    for k in {('M' + x) for x in re.findall(r'M(\d+)', mcell)}:
        a_M[k] = a_M.get(k, 0) + 1
    for k in {('S' + x) for x in re.findall(r'S(\d+)', scell)}:
        a_S[k] = a_S.get(k, 0) + 1
    real_m = len([x for x in mcell.split(';') if x.strip()])
    a_real_m_sum += real_m
    a_declared_m_sum += dec_m or 0
    a_biz[biz] = a_biz.get(biz, 0) + 1

print('=' * 90)
print('【T5A 独立复算】案例数 N =', a_n, '｜ 物料条目合计=', a_real_m_sum,
      '｜ 工蜂自报项数合计=', a_declared_m_sum)
print('业态分布 =', dict(sorted(a_biz.items(), key=lambda kv: -kv[1])))

# ============================================================
# 二、T5B 商业套餐样本（原始行重抽）
# ============================================================
tb = read('T5B-资料包-外部商业交付口径与报价样本.md')
b_rows = parse_table(tb, '## 二、样本总表', '## 三、')

b_n = 0
b_M, b_S = {}, {}
for r in b_rows:
    c = cells_of(r)
    if len(c) < 13:
        print('[T5B] 列数异常跳过:', len(c), r[:60]); continue
    b_n += 1
    mcell, scell = c[8], c[9]
    for k in {('M' + x) for x in re.findall(r'M(\d+)', mcell)}:
        b_M[k] = b_M.get(k, 0) + 1
    for k in {('S' + x) for x in re.findall(r'S(\d+)', scell)}:
        b_S[k] = b_S.get(k, 0) + 1

print()
print('【T5B 独立复算】套餐数 N =', b_n)

# ============================================================
# 三、实测基准（既有资产，不重验，采用 T3 已发布数字）
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
STRONG = 15.0


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
# 四、解析 T6 报告 §2.1 / §2.2 的「我复算值 vs T6报告值」
# ============================================================
t6 = read('T6-报告-外部样本与实测样本对撞.md')


def parse_collision(t6, header_marker):
    seg = t6.split(header_marker)[1]
    # 取到下一个 '###' 或 '##' 之前
    seg = re.split(r'\n###|\n## ', seg)[0]
    out = {}
    for line in seg.split('\n'):
        s = line.strip()
        if not s.startswith('|'):
            continue
        if re.fullmatch(r'\|[\s:|-]+\|', s):
            continue
        c = cells_of(s)
        code = c[0].replace('*', '').strip()
        if not re.match(r'^M\d+$', code) and not re.match(r'^S\d+$', code):
            continue
        # 实测/案例/套餐 在 c[2],c[3],c[4]; 判定在 c[5]
        def pct(x):
            x = x.replace('*', '').replace('%', '').strip()
            return float(x) if x not in ('',) else None
        out[code] = {
            '实测': pct(c[2]), '案例': pct(c[3]), '套餐': pct(c[4]),
            '判定': c[5].replace('*', '').strip()
        }
    return out


def _val(v):
    # 修正：0.0 是合法数值，不能用 `or -1`
    return v if v is not None else -1.0


t6_m = parse_collision(t6, '### 2.1 物料应用')
t6_s = parse_collision(t6, '### 2.2 场景应用')

print()
print('=' * 90)
print('【三、T6 §2.1/§2.2 对撞表 逐格比对】')
print('%-5s %-13s | %8s %8s %8s | %8s %8s %8s | %s' %
      ('码', '大类', '实测R', '案例R', '套餐R', '实测T', '案例T', '套餐T', '一致'))
all_ok = True
for k in M_ORDER:
    my = MY_M[k] / MY_B * 100
    ap = a_M.get(k, 0) / a_n * 100
    bp = b_M.get(k, 0) / b_n * 100
    t = t6_m.get(k, {})
    tmy, tap, tbp = t.get('实测'), t.get('案例'), t.get('套餐')
    ok = (abs(_val(tmy) - my) < 0.15 and abs(_val(tap) - ap) < 0.15
          and abs(_val(tbp) - bp) < 0.15)
    all_ok &= ok
    print('%-5s %-13s | %7.1f%% %7.1f%% %7.1f%% | %7.1f%% %7.1f%% %7.1f%% | %s' %
          (k, M_NAME[k], my, ap, bp, tmy or 0, tap or 0, tbp or 0, '✓' if ok else '✗ 不一致'))
for k in S_ORDER:
    my = MY_S[k] / MY_C * 100
    ap = a_S.get(k, 0) / a_n * 100
    bp = b_S.get(k, 0) / b_n * 100
    t = t6_s.get(k, {})
    tmy, tap, tbp = t.get('实测'), t.get('案例'), t.get('套餐')
    ok = (abs(_val(tmy) - my) < 0.15 and abs(_val(tap) - ap) < 0.15
          and abs(_val(tbp) - bp) < 0.15)
    all_ok &= ok
    print('%-5s %-13s | %7.1f%% %7.1f%% %7.1f%% | %7.1f%% %7.1f%% %7.1f%% | %s' %
          (k, S_NAME[k], my, ap, bp, tmy or 0, tap or 0, tbp or 0, '✓' if ok else '✗ 不一致'))
print('→ 24 格数值全部一致：', all_ok)

# ============================================================
# 五、三源判定标签复核（我的 verdict vs T6 判定列）
# ============================================================
print()
print('=' * 90)
print('【四、三源判定标签复核】')
print('%-5s | %-22s | %-22s | %s' % ('码', '我 verdict', 'T6 判定', '一致'))
label_ok = True
for k in M_ORDER + S_ORDER:
    my = MY_M[k] / MY_B * 100 if k.startswith('M') else MY_S[k] / MY_C * 100
    ap = (a_M.get(k, 0) / a_n * 100) if k.startswith('M') else (a_S.get(k, 0) / a_n * 100)
    bp = (b_M.get(k, 0) / b_n * 100) if k.startswith('M') else (b_S.get(k, 0) / b_n * 100)
    mv = verdict(my, ap, bp)
    t = (t6_m if k.startswith('M') else t6_s).get(k, {}).get('判定', '')
    # 归一化比较：剥离「X源 · 」前缀与「全强共振→三源共振」等价
    def norm(s):
        s = s.split('（')[0]  # 去掉「（极差 XXpt）」等批注
        s = s.replace('双源 · ', '').replace('单源 · ', '').replace('三源 · ', '')
        s = s.replace('全强共振', '三源共振')
        return s.strip()
    ok = norm(mv) == norm(t)
    label_ok &= ok
    print('%-5s | %-22s | %-22s | %s' % (k, mv, t, '✓' if ok else '✗'))

# ============================================================
# 六、T6 §三 数据打假 6 处（T5B 工蜂自报 vs 我复算）
# ============================================================
# T5B §五 工蜂自报表（从 T5B 原文抄录）
TB_SELF_M = {'M1': 20, 'M2': 0, 'M3': 5, 'M4': 8, 'M5': 1, 'M6': 0, 'M7': 3, 'M8': 9,
             'M9': 9, 'M10': 10, 'M11': 5, 'M12': 0, 'M13': 11, 'M14': 0, 'M15': 0}
# T6 §三 声称的更正（以复算值为准）
T6_CLAIM = {'M3': (5, 4), 'M4': (8, 9), 'M7': (3, 2), 'M8': (9, 10), 'M9': (9, 7), 'M13': (11, 12)}

print()
print('=' * 90)
print('【五、T6 §三 打假记录 6 处 校验】')
print('%-5s | 工蜂自报 | 我复算 | T6声称复算 | 三源打假成立?')
fake_ok = True
for k, (sv, cv) in T6_CLAIM.items():
    mv = b_M.get(k, 0)
    # 是否成立：工蜂自报(sv) != 我复算(mv)，且 T6 声称复算值(cv) == 我复算(mv)
    bees_wrong = (sv != mv)
    t6_right = (cv == mv)
    established = bees_wrong and t6_right
    fake_ok &= established
    print('%-5s | %8d | %6d | %10d | %s' % (k, sv, mv, cv,
          '✓ 成立' if established else ('✗ T6改错' if (sv != mv and not t6_right) else '✗ 工蜂没错')))
print('→ 6 处打假全部成立（蜂王更正无误）：', fake_ok)

# ============================================================
# 七、§2.3 / §〇 汇总计数复核
# ============================================================
print()
print('=' * 90)
print('【六、§2.3 / §〇 汇总计数复核】')
# 按 T6 规则归桶（全强共振并入三源共振；标签取 ★/◆/三源皆无/单源）
buckets = {'三源共振': 0, '★我有外弱': 0, '◆我缺口': 0, '单源': 0, '三源皆无': 0}
items = {'三源共振': [], '★我有外弱': [], '◆我缺口': [], '单源': [], '三源皆无': []}
for k in M_ORDER + S_ORDER:
    my = MY_M[k] / MY_B * 100 if k.startswith('M') else MY_S[k] / MY_C * 100
    ap = (a_M.get(k, 0) / a_n * 100) if k.startswith('M') else (a_S.get(k, 0) / a_n * 100)
    bp = (b_M.get(k, 0) / b_n * 100) if k.startswith('M') else (b_S.get(k, 0) / b_n * 100)
    v = verdict(my, ap, bp)
    if v == '三源皆无':
        b = '三源皆无'
    elif '★我有外弱' in v:
        b = '★我有外弱'
    elif '◆我缺口' in v:
        b = '◆我缺口'
    elif '单源' in v:
        b = '单源'
    else:
        b = '三源共振'
    buckets[b] += 1
    items[b].append(k)
for b in ['三源共振', '★我有外弱', '◆我缺口', '单源', '三源皆无']:
    print('%-12s 计数=%d  类目=%s' % (b, buckets[b], ' '.join(items[b])))
print('合计 =', sum(buckets.values()), '(应为 24)')
print('T6 §〇/§2.3 声称：三源共振10 / ★我有外弱7 / ◆我缺口5 / 单源2 / 三源皆无1')
print('→ ★我有外弱应为 6（29.2%% 应为 25.0%%）；§〇/§2.3 合计 25 ≠ 24：',
      '✗ 计数错误' if buckets['★我有外弱'] != 7 else '✓')
print()
print('复算完毕。')
