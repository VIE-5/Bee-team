# -*- coding: utf-8 -*-
"""v5 · 物料应用段落改造（29 张 → 14 页）

把原 P19–P24（6 页，每页 1 张拼图）替换为 14 页独立物料展示。
后续原 P25–P37 页码 +8。总页数 37 → 45。

主人要求（2026-09-22）：
  ① 用「独立物料」目录（29 张）替换物料应用部分
  ② 不拼图，改为独立展示
  ③ 禁止页眉页脚冲突（图片限内容区）
  ④ 禁止景深 / 渐变 / 遮罩

文案来源：原册文案 + 素材图上原文，零编造。
"""
import io
import os
import re

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
HTML = os.path.join(BASE, 'index.html')
BAK = os.path.join(BASE, 'index-v4-bak.html')

SH = ('肆', '空间与器物')
KJ = ('伍', '空间应用')

PAGES = [
    dict(chap=SH, h='客用器物与餐具', en='Tableware &amp; Dining Utensils',
         cap='山水线描 · 暖米白底 · 墨绿描边',
         cells=[('mat-01', '客用餐具', '骨瓷 · 暖米白底 · 山水线描收口'),
                ('mat-08', '餐具更多系列', '壶 · 杯 · 小碟 · 分餐件')],
         badge='TABLEWARE', note='一院烟火味，岭南土蚝鲜'),
    dict(chap=SH, h='餐具配套细件', en='Dining Accessories',
         cap='墨绿 · 米白 双色体系',
         cells=[('mat-02', '筷套', '墨绿 / 米白双款 · 正背两面'),
                ('mat-03', '牙签套', '一签小巧 · 亦是生活的滋味')],
         badge='ACCESSORIES', note='一双好筷，夹起岭南好味'),
    dict(chap=SH, h='桌面纸品耗材', en='Table Paper Goods',
         cap='深绿底 · 反白标志',
         cells=[('mat-04', '餐巾纸盒', '台面抽纸 · 深绿底反白标志'),
                ('mat-05', '湿巾纸', '净手亦净心 · 好味更安心')],
         badge='PAPER GOODS', note='净手亦净心，好味更安心'),
    dict(chap=SH, h='桌面配套与纸杯', en='Accessories &amp; Paper Cups',
         cap='一院烟火味 · 点亮好时光',
         cells=[('mat-06', '打火机', '墨绿款 / 米白款 · 一院烟火味'),
                ('mat-07', '外带杯 · 堂食杯', '含杯盖 / 标志 / 图案 / 材质细节')],
         badge='ACCESSORIES', note='一杯烟火味，盛满岭南鲜'),
    dict(chap=SH, h='会员与卡券体系', en='Membership &amp; Vouchers',
         cap='双面呈现 · 权益清晰',
         cells=[('mat-13', '优惠券', '满减券 · 满额可用'),
                ('mat-14', '会员卡', '充值卡 · 双面（墨绿 / 米白）')],
         badge='MEMBERSHIP', note='尊享美味，会员专属，更多权益'),
    dict(chap=SH, h='订餐卡与打包盒', en='Reservation Card &amp; Takeaway Box',
         cap='一份心意 · 一院风味',
         cells=[('mat-15', '订餐卡', '美味提前约，小院等您来'),
                ('mat-16', '打包盒', '方盒大中小号 + 汤品桶')],
         badge='PACKAGING', note='一份心意，一院风味'),
    dict(chap=SH, h='打包袋与礼品袋', en='Takeaway &amp; Gift Bags',
         cap='牛皮质朴 · 墨绿雅致',
         cells=[('mat-18', '打包袋', '牛皮纸 / 墨绿双款 · 提绳工艺'),
                ('mat-19', '礼品袋', '墨绿工艺 · 食在岭南，相聚小院')],
         badge='PACKAGING', note='食在岭南，相聚小院'),
    dict(chap=SH, h='封口标签与筷套', en='Seals &amp; Chopstick Sleeves',
         cap='封签已开 · 美味即来',
         cells=[('mat-17', '打包标签', '圆形封口贴 · 长条封口贴 · 牛皮贴纸'),
                ('mat-20', '筷套与餐具套装', '筷套正背两面 · 内含 1 双筷子')],
         badge='PACKAGING', note='以食为媒，邀你入院'),
    dict(chap=SH, h='档口与客流物料', en='Service &amp; Guest Touchpoints',
         cap='四款形态 · 统一规范',
         cells=[('mat-25', '台号牌', '四款形态 · 墨绿 / 米白 / 圆形 / 异形'),
                ('mat-26', '桌面立牌', '正面品牌宣传 · 背面扫码引导'),
                ('mat-27', '员工工牌', '姓名 + 岗位编号 · 统一规范')],
         badge='TOUCHPOINTS', note='东方意境，清晰雅致', cls='c3'),
    dict(chap=SH, h='员工服饰规范', en='Staff Uniform',
         cap='中式盘扣 · 刺绣标志',
         cells=[('mat-28', '服务员服装', '含面料与细节 · 台前服务'),
                ('mat-29', '厨师服装', '含面料与细节 · 厨务专业')],
         badge='UNIFORM', note='台前幕后，东方气韵'),
    dict(chap=KJ, h='名片与门店招牌', en='Business Card &amp; Storefront',
         cap='东方美学 · 立体字工艺',
         cells=[('mat-09', '名片', '质感纸张 · 双面 · 东方美学'),
                ('mat-10', '门头招牌', '金属质地 · 胡桃木边框 · 立体字')],
         badge='ENTRANCE', note='匠心工艺 · 东方韵味'),
    dict(chap=KJ, h='玻璃防撞贴与门帘', en='Glass Decals &amp; Door Curtain',
         cap='覆盖宾客动线每一处',
         cells=[('mat-11', '玻璃防撞贴', '大厅门贴 · 隔断贴 · 门口贴'),
                ('mat-12', '门帘', '布艺配版 · 山水线描 · 东方意境')],
         badge='ENTRANCE', note='食在山水间，心归小院里'),
    dict(chap=KJ, h='营业与功能提示牌', en='Operating &amp; Function Signage',
         cap='材质并行 · 功能亦雅致',
         cells=[('mat-21', '营业时间牌', '实木挂牌 / 台牌 / 悬挂式门牌'),
                ('mat-22', '区域牌', '自助小吃 · 厨房 · 收银台 · 就餐区 · 洗手间')],
         badge='SIGNAGE', note='一院烟火味，岭南好滋味'),
    dict(chap=KJ, h='包间门牌与温馨提示', en='Room Plaques &amp; Notice Signs',
         cap='一院一景 · 各有其名',
         cells=[('mat-23', '包间门牌', '春山 · 听竹 · 观澜 · 映月'),
                ('mat-24', '温馨提示牌', '免费 WiFi · 保管财物 · 请勿吸烟 · 小心地滑')],
         badge='SIGNAGE', note='东方意境，清晰雅致'),
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
      <div class="t-cap" style="letter-spacing:var(--ls-wide)">{cap}</div>
    </div>
    <div class="mat-pair{cls}">
{cells}    </div>
  </div>
  <footer class="ft">
    <span class="badge">{badge}</span>
    <span class="note">{note}</span>
  </footer>
  <div class="pg">{pg}</div>
</section>
"""

CELL = """      <figure class="mat-cell">
        <div class="ph"><img src="assets/{k}.webp" alt="{t}"></div>
        <figcaption>
          <b>{t}</b>
          <span>{d}</span>
        </figcaption>
      </figure>
"""


def main():
    html = io.open(BAK, encoding='utf-8').read()
    secs = [(m.start(), m.end()) for m in
            re.finditer(r'<section class="slide[^>]*>.*?</section>', html, re.S)]
    assert len(secs) == 37, '备份 section 数异常: %d' % len(secs)

    for i in range(18, 24):
        m = re.search(r'<div class="pg">(\d+)</div>', html[secs[i][0]:secs[i][1]])
        assert m and int(m.group(1)) == i + 1, 'P%d 位置异常' % (i + 1)
    print('P19–P24 位置校验通过')

    cut = html.rfind('<!--', 0, secs[18][0])
    assert cut > 0
    before, after = html[:cut], html[secs[23][1]:]

    n = [0]

    def bump(m):
        num = int(m.group(1))
        if num >= 25:
            n[0] += 1
            return 'P%d ·' % (num + 8)
        return m.group(0)

    after = re.sub(r'P(\d{1,2}) ·', bump, after)
    print('after 段注释 +8 处数:', n[0])

    mid = []
    used = []
    for idx, p in enumerate(PAGES, 1):
        pg = 18 + idx
        cells = ''.join(CELL.format(k=k, t=t, d=d) for k, t, d in p['cells'])
        used += [k for k, _, _ in p['cells']]
        mid.append(SEC.format(pg=pg, h=p['h'], en=p['en'], cap=p['cap'],
                              cnum=p['chap'][0], cname=p['chap'][1],
                              cls=(' ' + p['cls']) if p.get('cls') else '',
                              cells=cells, badge=p['badge'], note=p['note']))
        print('  P%-3d %-22s %d 张  %s' % (pg, p['h'], len(p['cells']),
                                           ','.join(k for k, _, _ in p['cells'])))

    html2 = before + '\n'.join(mid) + after

    # 整体重编 .pg
    out, last = [], 0
    for i, m in enumerate(re.finditer(r'<section class="slide[^>]*>.*?</section>', html2, re.S), 1):
        chunk = html2[last:m.end()]
        out.append(re.sub(r'(<div class="pg">)\d+(</div>)', r'\g<1>%d\g<2>' % i, chunk, count=1))
        last = m.end()
    html3 = ''.join(out) + html2[last:]

    io.open(HTML, 'w', encoding='utf-8', newline='\n').write(html3)

    # 覆盖核对
    allmat = sorted(set(re.findall(r'src="assets/(mat-\d+)\.webp"', html3)))
    print('-' * 62)
    print('页面引用 mat-* 张数: %d' % len(allmat))
    missing = [m for m in ('mat-%02d' % i for i in range(1, 30)) if m not in allmat]
    print('缺失:', missing if missing else '无')
    unused = [k for k in used if k not in allmat]
    print('定义但未写入:', unused if unused else '无')
    print('已写入 index.html, 长度:', len(html3))


if __name__ == '__main__':
    main()
