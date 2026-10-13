# -*- coding: utf-8 -*-
"""v6 · 物料应用段落改造：29 张 → 29 页（单种物料单张独立成页）

主人 2026-09-22 纠正决策：
  「单种物料单张展示，不用组合展示」
  —— 取代 v5 的「每页 2 张并置」（14 页）。

做法：从 v4 备份（37 页）重建 ——
  切掉原 P19–P24（6 页拼图），插入 29 页单张展示；
  后续原 P25–P37（13 页）注释页码 +23 → P48–P60；总页数 37 → 60。

硬约束（沿用 v5）：
  ① 不拼图，独立展示        ② 禁止页眉页脚冲突（图限内容区）
  ③ 禁止景深 / 渐变 / 遮罩

文案来源：原册文案 + 素材图上原文，零编造。
"""
import io
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE, '01-工蜂产出', 'assets')
HTML = os.path.join(BASE, '01-工蜂产出', 'index.html')
BAK = os.path.join(BASE, '_中间文件', '_备份', 'index-v4-bak.html')

SH = ('肆', '空间与器物')
KJ = ('伍', '空间应用')

# (章, 素材号, 中文名, 英文名, 描述, 页脚徽章, 页脚注)
ITEMS = [
    # ——— 肆 · 空间与器物 ———
    (SH, 'mat-01', '客用餐具', 'Dining Utensils',
     '骨瓷 · 暖米白底 · 山水线描收口', 'TABLEWARE', '一院烟火味，岭南土蚝鲜'),
    (SH, 'mat-08', '餐具更多系列', 'Utensil Series',
     '壶 · 杯 · 小碟 · 分餐件 · 同源图形延展', 'TABLEWARE', '一院烟火味，岭南土蚝鲜'),
    (SH, 'mat-02', '筷套', 'Chopstick Sleeve',
     '墨绿 / 米白双款 · 正背两面', 'ACCESSORIES', '一双好筷，夹起岭南好味'),
    (SH, 'mat-03', '牙签套', 'Toothpick Sleeve',
     '一签小巧 · 亦是生活的滋味', 'ACCESSORIES', '一签小巧，亦是生活的滋味'),
    (SH, 'mat-04', '餐巾纸盒', 'Napkin Box',
     '台面抽纸 · 深绿底反白标志', 'PAPER GOODS', '净手亦净心，好味更安心'),
    (SH, 'mat-05', '湿巾纸', 'Wet Wipe',
     '独立包装 · 净手亦净心', 'PAPER GOODS', '净手亦净心，好味更安心'),
    (SH, 'mat-06', '打火机', 'Lighter',
     '墨绿款 / 米白款 · 一院烟火味', 'ACCESSORIES', '一杯烟火味，盛满岭南鲜'),
    (SH, 'mat-07', '外带杯 · 堂食杯', 'Paper Cups',
     '含杯盖 / 标志 / 图案 / 材质细节', 'ACCESSORIES', '一杯烟火味，盛满岭南鲜'),
    (SH, 'mat-13', '优惠券', 'Vouchers',
     '满减券 · 满额可用 · 双面呈现', 'MEMBERSHIP', '尊享美味，会员专属'),
    (SH, 'mat-14', '会员卡', 'Membership Card',
     '充值卡 · 双面（墨绿 / 米白）', 'MEMBERSHIP', '尊享美味，会员专属'),
    (SH, 'mat-15', '订餐卡', 'Reservation Card',
     '美味提前约，小院等您来', 'PACKAGING', '一份心意，一院风味'),
    (SH, 'mat-16', '打包盒', 'Takeaway Box',
     '方盒大中小号 + 汤品桶', 'PACKAGING', '一份心意，一院风味'),
    (SH, 'mat-18', '打包袋', 'Takeaway Bag',
     '牛皮纸 / 墨绿双款 · 提绳工艺', 'PACKAGING', '食在岭南，相聚小院'),
    (SH, 'mat-19', '礼品袋', 'Gift Bag',
     '墨绿工艺 · 食在岭南，相聚小院', 'PACKAGING', '食在岭南，相聚小院'),
    (SH, 'mat-17', '打包标签', 'Sealing Labels',
     '圆形封口贴 · 长条封口贴 · 牛皮贴纸', 'PACKAGING', '以食为媒，邀你入院'),
    (SH, 'mat-20', '筷套与餐具套装', 'Chopstick Set',
     '筷套正背两面 · 内含 1 双筷子', 'PACKAGING', '以食为媒，邀你入院'),
    (SH, 'mat-25', '台号牌', 'Table Number Signs',
     '四款形态 · 墨绿 / 米白 / 圆形 / 异形', 'TOUCHPOINTS', '东方意境，清晰雅致'),
    (SH, 'mat-26', '桌面立牌', 'Table Tent',
     '正面品牌宣传 · 背面扫码引导', 'TOUCHPOINTS', '东方意境，清晰雅致'),
    (SH, 'mat-27', '员工工牌', 'Staff Name Badge',
     '姓名 + 岗位编号 · 统一规范', 'TOUCHPOINTS', '台前幕后，东方气韵'),
    (SH, 'mat-28', '服务员服装', 'Service Uniform',
     '中式盘扣 · 刺绣标志 · 台前服务', 'UNIFORM', '台前幕后，东方气韵'),
    (SH, 'mat-29', '厨师服装', 'Chef Uniform',
     '含面料与细节 · 厨务专业', 'UNIFORM', '台前幕后，东方气韵'),
    # ——— 伍 · 空间应用 ———
    (KJ, 'mat-09', '名片', 'Business Card',
     '质感纸张 · 双面 · 东方美学', 'ENTRANCE', '匠心工艺 · 东方韵味'),
    (KJ, 'mat-10', '门头招牌', 'Storefront Signage',
     '金属质地 · 胡桃木边框 · 立体字', 'ENTRANCE', '匠心工艺 · 东方韵味'),
    (KJ, 'mat-11', '玻璃防撞贴', 'Glass Decals',
     '大厅门贴 · 隔断贴 · 门口贴', 'ENTRANCE', '食在山水间，心归小院里'),
    (KJ, 'mat-12', '门帘', 'Door Curtain',
     '布艺配版 · 山水线描 · 东方意境', 'ENTRANCE', '食在山水间，心归小院里'),
    (KJ, 'mat-21', '营业时间牌', 'Opening Hours Sign',
     '实木挂牌 / 台牌 / 悬挂式门牌', 'SIGNAGE', '一院烟火味，岭南好滋味'),
    (KJ, 'mat-22', '区域牌', 'Area Signs',
     '自助小吃 · 厨房 · 收银台 · 就餐区 · 洗手间', 'SIGNAGE', '一院烟火味，岭南好滋味'),
    (KJ, 'mat-23', '包间门牌', 'Room Plaques',
     '春山 · 听竹 · 观澜 · 映月', 'SIGNAGE', '东方意境，清晰雅致'),
    (KJ, 'mat-24', '温馨提示牌', 'Notice Signs',
     '免费 WiFi · 保管财物 · 请勿吸烟 · 小心地滑', 'SIGNAGE', '东方意境，清晰雅致'),
]

SEC = """<!-- ══════════════════════════════════════════════════════════
     P{pg} · {h}
     ══════════════════════════════════════════════════════════ -->
<section class="slide">
  <header class="hd">
    <div class="brand">土蚝小院<em>TUHAO XIAOYUAN</em></div>
    <i></i>
    <div class="chap"><b>{cnum}</b>{cname}</div>
  </header>
  <div class="bd" style="justify-content:center">
    <div class="mat-head">
      <div>
        <div class="sec-h">{h}</div>
        <div class="sec-en">{en}</div>
      </div>
    </div>
    <div class="mat-single">
      <figure class="mat-cell">
        <div class="ph"><img src="assets/{k}.webp" alt="{h}"></div>
        <figcaption>
          <span>{d}</span>
        </figcaption>
      </figure>
    </div>
  </div>
  <footer class="ft">
    <span class="badge">{badge}</span>
    <span class="note">{note}</span>
  </footer>
  <div class="pg">{pg}</div>
</section>
"""


def main():
    assert os.path.isfile(BAK), '备份缺失: %s' % BAK
    html = io.open(BAK, encoding='utf-8').read()
    secs = [(m.start(), m.end()) for m in
            re.finditer(r'<section class="slide[^>]*>.*?</section>', html, re.S)]
    assert len(secs) == 37, '备份 section 数异常: %d' % len(secs)

    for i in range(18, 24):
        m = re.search(r'<div class="pg">(\d+)</div>', html[secs[i][0]:secs[i][1]])
        assert m and int(m.group(1)) == i + 1, 'P%d 位置异常' % (i + 1)
    print('P19-P24 位置校验通过 (37 页备份)')

    # 素材存在性预检
    miss = [k for _, k, _, _, _, _, _ in ITEMS
            if not os.path.isfile(os.path.join(ASSETS, k + '.webp'))]
    assert not miss, '素材缺失: %s' % miss
    print('29 张素材文件齐备')

    assert len(ITEMS) == 29, '条目数异常: %d' % len(ITEMS)
    assert len({k for _, k, _, _, _, _, _ in ITEMS}) == 29, '素材号有重复'

    cut = html.rfind('<!--', 0, secs[18][0])
    assert cut > 0
    before, after = html[:cut], html[secs[23][1]:]

    N = len(ITEMS)          # 29
    SHIFT = N - 6           # 23 —— 后续 13 页注释整体 +23

    n = [0]

    def bump(m):
        num = int(m.group(1))
        if num >= 25:
            n[0] += 1
            return 'P%d ·' % (num + SHIFT)
        return m.group(0)

    after = re.sub(r'P(\d{1,2}) ·', bump, after)
    print('after 段注释 +%d 处数: %d  (期望 13)' % (SHIFT, n[0]))
    assert n[0] == 13, '后续注释命中数异常: %d' % n[0]

    mid = []
    for idx, (chap, k, h, en, d, badge, note) in enumerate(ITEMS, 1):
        pg = 18 + idx
        mid.append(SEC.format(pg=pg, h=h, en=en, d=d, k=k,
                              cnum=chap[0], cname=chap[1],
                              badge=badge, note=note))
    print('生成 %d 页单张展示 (P19-P%d)' % (N, 18 + N))

    html2 = before + '\n'.join(mid) + after

    # 整体重编 .pg
    out, last = [], 0
    for i, m in enumerate(re.finditer(r'<section class="slide[^>]*>.*?</section>', html2, re.S), 1):
        chunk = html2[last:m.end()]
        out.append(re.sub(r'(<div class="pg">)\d+(</div>)', r'\g<1>%d\g<2>' % i, chunk, count=1))
        last = m.end()
    html3 = ''.join(out) + html2[last:]

    io.open(HTML, 'w', encoding='utf-8', newline='\n').write(html3)

    # ——— 覆盖核对 ———
    nsec = len(re.findall(r'<section class="slide', html3))
    allmat = sorted(set(re.findall(r'src="assets/(mat-\d+)\.webp"', html3)))
    want = sorted({'mat-%02d' % i for i in range(1, 30)})
    print('-' * 62)
    print('总页数        : %d  (期望 60)' % nsec)
    print('引用 mat-* 数 : %d  (期望 29)' % len(allmat))
    print('缺失          : %s' % ([m for m in want if m not in allmat] or '无'))
    print('多出          : %s' % ([m for m in allmat if m not in want] or '无'))
    print('残留 .mat-pair: %d  (期望 0)' % len(re.findall(r'class="mat-pair', html3)))
    print('引用 .mat-single: %d  (期望 29)' % len(re.findall(r'class="mat-single"', html3)))


if __name__ == '__main__':
    main()
