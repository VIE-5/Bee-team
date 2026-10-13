# -*- coding: utf-8 -*-
"""T3 / W3 图片施工蜂（C 线）—— A4 竖版书册生成器。
输入 : 01-工蜂产出/T1-资料包-原著结构化数据集.json
输出 : 01-工蜂产出/T3-版式/index.html
画布 : 794 x 1123 px (A4 @96dpi, ratio 0.7071)
"""
import html
import json
import math
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "01-工蜂产出" / "T1-资料包-原著结构化数据集.json").read_text(encoding="utf-8"))
OUT = ROOT / "01-工蜂产出" / "T3-版式" / "index.html"
OUT.parent.mkdir(parents=True, exist_ok=True)

# ---------- 几何常量（固定画布一律硬编码 px · R7） ----------
W, H = 794, 1123
MX = 76
HD, FT = 96, 64
CW = W - 2 * MX          # 642
CH = H - HD - FT         # 963
BUDGET = CH - 10  # 分页预算（卡片高度为浏览器实测值，留 10px 余量）
GAP = 14

# 浏览器实测的卡片高度（由 _measure.html 回传；缺失则退回估算）
HJSON = ROOT / "_work" / "card_heights.json"
try:
    REAL = json.loads(HJSON.read_text(encoding="utf-8"))
except Exception:
    REAL = {}

# 2026-10-10 第二轮：主人要求全书改名。
#   书名由「高性价比人生指南」→「失足大学生误入职场魔窟求生指南」
#   ⚠️ 页脚署名 BRAND 仍保留**原著书名**：CC BY 4.0 要求署名含「作者 + 作品名 + 来源 + 许可」，
#      换标题后若把原著书名一起抹掉，就构成署名缺失（尾页「来源与许可」本轮已按主人要求删除，
#      署名全靠页脚与封面承载）。
TITLE = "失足大学生误入职场魔窟求生指南"          # 书名（页眉左 / <title>）
TITLE_LINES = ["失足大学生", "误入职场魔窟", "求生指南"]   # 封面三行断行
BRAND = "原著《高性价比人生指南》· eternity4719/HowToLiveBetter · CC BY 4.0"
if "".join(TITLE_LINES) != TITLE:
    raise SystemExit("!! 封面断行拼接与 TITLE 不一致 —— 改名时请同步 TITLE_LINES")

# ---------- 数据筛选与分组 ----------
def is_top(e):
    t = e["tags"]
    return (t.get("钱") == "0" and t.get("时间") == "少"
            and t.get("毅力") == "否" and t.get("收益") == "大")


SEL = [e for e in DATA["entries"] if is_top(e)]
KJ = {"死亡率": "health", "金钱": "money", "自由": "freedom", "时间": "time"}
PIAN = OrderedDict([
    ("health",  {"no": "壹", "name": "健康与寿命", "en": "HEALTH & LONGEVITY",
                 "lead": "活得久、少生病，是性价比最高的一笔投资。这一篇里的建议，几乎不花一分钱，也不用额外挤时间——换回的是死亡风险实打实的下降。"}),
    ("money",   {"no": "贰", "name": "金钱", "en": "MONEY",
                 "lead": "真正省下钱的不是抠，而是不踩坑。这一篇里每条都写明了花掉什么、换回什么；照做与不做，差的往往是几百到几万元。"}),
    ("freedom", {"no": "叁", "name": "人身自由", "en": "PERSONAL FREEDOM",
                 "lead": "一条不知道的法律红线，就可能把自己送进拘留所。这一篇不看成本，只看后果——防的是「把自己搭进去」。"}),
    ("time",    {"no": "肆", "name": "时间与精力", "en": "TIME & ENERGY",
                 "lead": "每天被浪费掉的时间和精力，比浪费掉的钱更难察觉。这一篇里的几条，几乎立刻见效。"}),
])

pian_map = defaultdict(lambda: OrderedDict())   # key -> OrderedDict(sec_no -> [entries])
for e in SEL:
    pian_map[KJ[e["tags"]["口径"]]].setdefault(e["sec_no"], []).append(e)

SECNAME = {s["sec_no"]: s["sec_name"] for s in DATA["sections"]}
GRADE = lambda g: g.split("（")[0]
KJCN = {"health": "健康与寿命", "money": "金钱", "freedom": "人身自由", "time": "时间与精力"}


# ---------- 文本度量 ----------
def cjk_w(s):
    return sum(1.0 if ord(c) > 0x2E80 else 0.53 for c in s)


def nlines(s, fs, w):
    if not s:
        return 1
    return max(1, math.ceil(cjk_w(s) / (w / fs)))


def esc(s):
    return html.escape(s, quote=False)


def compact_source(s):
    import re
    s = re.sub(r"<[^>]+>", "", s)          # 去 URL
    s = re.sub(r"\s+", " ", s).strip()
    s = s.rstrip(". ").strip()
    if len(s) > 165:
        s = s[:165].rstrip() + "…"
    return s


# ---------- 卡片 ----------
def card_h(e):
    """估算值（只作兜底）—— 正式分页一律用 REAL（浏览器实测值）。"""
    k = "%d:%d" % (e["sec_no"], e["idx"])
    if k in REAL:
        return REAL[k]
    h = 13 + 13                        # .cd 上下内边距
    h += nlines(e["title"], 16, 486) * 22      # 标题（已扣条号栏 + 徽章宽）
    h += 7                             # .cd-b 上边距
    h += nlines(e["plain"], 13, 530) * 20.5 + 18   # 说人话（高亮块 + 内边距）
    h += 9 + 17                        # 标注行
    src = compact_source(e["source"])
    h += 7 + min(nlines(src, 9, 560), 3) * 13.5    # 出处
    return h


def card_html(e):
    """条目卡 —— 「分条」版式：左侧悬挂条号（带竖分隔线），内容右对齐同一列；
    证据徽章提到标题行右端（可一眼扫），说人话为主读块，成本/换回为结构化标注行。"""
    g = GRADE(e["grade"])
    k = KJ[e["tags"]["口径"]]
    kj = KJCN[k]
    return (
        '<article class="cd">'
        '<div class="cd-h">'
        '<span class="cd-n">%02d</span>'
        '<h3 class="cd-t">%s</h3>'
        '<span class="badge g-%s">证据 %s</span>'
        '</div>'
        '<div class="cd-b">'
        '<div class="cd-p"><span class="cd-pl">说人话</span>%s</div>'
        '<div class="cd-m">'
        '<span class="cd-mi v-%s"><i>换回</i>%s</span>'
        '<span class="cd-mi"><i>成本</i>不花钱 · 不占时间 · 不需毅力</span>'
        '</div>'
        '<div class="cd-s"><span class="cd-sk">出处</span>%s</div>'
        '</div>'
        '</article>'
    ) % (e["idx"], esc(e["title"]), g, g, esc(e["plain"]),
         k, kj, esc(compact_source(e["source"])))


def sec_h():
    return 31


def sec_html(sec_no):
    n = len([1 for k in pian_map.values() for e in k.get(sec_no, [])])
    return ('<div class="sec"><span class="sec-n">%02d</span>'
            '<span class="sec-t">%s</span></div>') % (sec_no, esc(SECNAME[sec_no]))


# ---------- 分页 ----------
def gapof(b):
    """块的『上边距』——节标题 30px，其余 14px（与 theme_a4.css 的 .ct 规则一一对应）。"""
    return 30 if b["kind"] == "sec" else GAP


def build_body():
    pages = []
    for key, secs in pian_map.items():
        pages.append({"kind": "part", "pian": key, "blocks": []})
        blocks = []
        for sec_no in sorted(secs.keys()):
            blocks.append({"kind": "sec", "sec": sec_no, "h": sec_h()})
            for e in secs[sec_no]:
                blocks.append({"kind": "card", "h": card_h(e), "e": e})
        cur, curh = [], 0
        for b in blocks:
            h = b["h"] + (gapof(b) if cur else 0)
            if cur and curh + h > BUDGET:
                if cur[-1]["kind"] == "sec" and len(cur) > 1:
                    tail = cur.pop()
                    pages.append({"kind": "entries", "pian": key, "blocks": cur})
                    cur, curh = [tail], tail["h"]
                else:
                    pages.append({"kind": "entries", "pian": key, "blocks": cur})
                    cur, curh = [], 0
                h = b["h"] + (gapof(b) if cur else 0)
            cur.append(b)
            curh += h
        if cur:
            pages.append({"kind": "entries", "pian": key, "blocks": cur})
    return pages


body = build_body()
# 2026-10-10 第二轮：序页与尾页已删 → 总页数 = 封面 1 + 目录 1 + body
TOTAL = 2 + len(body)

# 页码登记（两遍法）
# ⚠️ sec_page 必须以 (篇, 节号) 为键：同一节的内容可能同时归属两篇
#    （如「反面清单」的条目分别换回健康与金钱）→ 按节号单键登记会让目录
#    在第二篇下显示第一篇的页码。2026-10-10 实测：40 条目录行错 11 条。
pian_page, sec_page = {}, {}
for i, p in enumerate(body):
    pno = 3 + i          # 封面 P1 · 目录 P2 · body 从 P3 起
    if p["kind"] == "part":
        pian_page[p["pian"]] = pno
    for b in p["blocks"]:
        if b["kind"] == "sec":
            sec_page.setdefault((p["pian"], b["sec"]), pno)


# ---------- 页面渲染 ----------
def head(page_no, right, dark=False):
    return (
        '<header class="hd"><span class="hd-l">%s</span>'
        '<i class="hd-sep"></i><span class="hd-c">%s</span>'
        '<span class="hd-r">EVIDENCE&#8209;BASED</span></header>'
    ) % (TITLE, right)


def foot(page_no, dark=False):
    return ('<footer class="ft"><span class="ft-l">%s</span>'
            '<span class="ft-r">%d <em>/</em> %d</span></footer>') % (BRAND, page_no, TOTAL)


def page_shell(inner, cls="", page_no=None, hdr=None, dark=False):
    body = ""
    if hdr is not None:
        body += head(page_no, hdr)
    body += inner
    if page_no is not None:
        body += foot(page_no)
    return '<section class="slide %s%s" style="display:none">%s</section>' % (cls, " dark" if dark else "", body)


def cover():
    inner = (
        '<div class="cover">'
        '<div class="cv-kicker">EVIDENCE&#8209;BASED SURVIVAL GUIDE</div>'
        '<h1 class="cv-t">%s<br>%s<br><em>%s</em></h1>'
        '<div class="cv-rule"></div>'
        '<div class="cv-sub">蒸馏版 · 极高性价比精选</div>'
        '<div class="cv-big"><b>114</b><span>/ 676 条</span></div>'
        '<div class="cv-line">不花钱 · 不占时间 · 不需要毅力 · 收益最大</div>'
        '<div class="cv-foot">原著《高性价比人生指南》· <b>eternity4719/HowToLiveBetter</b> · 正文许可 CC BY 4.0<br>'
        '非官方节选蒸馏版本 · 2026-10-10 生成</div>'
        '</div>'
    ) % tuple(TITLE_LINES)
    return page_shell(inner, cls="pg-cover", dark=True)


def preface():
    rows = "".join(
        '<tr><td class="g">%s</td><td>%s</td></tr>' % (g, d) for g, d in [
            ("A", "有具体数字可查，出处是荟萃分析、大型队列或随机对照试验（RCT），能说出降了多少。"),
            ("B", "有研究支持，但说不出一个确切数字；或只有小样本、单项研究撑着。"),
            ("C", "作者经验或大家公认的做法，没有直接的研究文献。"),
        ])
    inner = (
        '<div class="pf">'
        '<h2 class="pf-h">怎么用这本册子</h2>'
        '<div class="pf-rule"></div>'
        '<p class="pf-lead">这不是一本书的浓缩摘要，而是一次<strong>按「性价比」执行的筛选</strong>：'
        '把原著 676 条里**不花钱、不占时间、不需要毅力，而收益最大**的那一档抽出来，共 <strong>114 条</strong>。</p>'
        '<div class="pf-grid">'
        '<div class="pf-card"><h4>筛选口径</h4>'
        '<p>同时满足四条：钱 = 0、时间 = 少、毅力 = 否、收益 = 大。这是原书自评的「性价比极高」档。</p></div>'
        '<div class="pf-card"><h4>四种资源</h4>'
        '<p>原著按四样东西算账：<b>寿命</b>、<b>时间与精力</b>、<b>金钱</b>、<b>人身自由</b>。四者各算各的，不互相折算。</p></div>'
        '</div>'
        '<h4 class="pf-h4">证据分级</h4>'
        '<table class="pf-tb">%s</table>'
        '<div class="pf-tip"><b>怎么读：</b>每条先看标题（做什么），再看「说人话」（关键结论），'
        '右下角是证据等级与出处。<b>不用全做</b>——挑一两条就算数，需要时再回来查。</div>'
        '<p class="pf-note">本册为原著的非官方节选蒸馏版：仅节选「极高性价比」条目并重排版式，'
        '<b>文字内容未作改写</b>；完整 676 条、逐条核实记录与原始文献链接见原著仓库。</p>'
        '</div>'
    ) % rows
    inner = inner.replace("**", "")
    return page_shell(inner, cls="pg-preface", page_no=2, hdr="序 · 怎么用")


def toc():
    cols = [[], []]
    keys = list(pian_map.keys())
    for ci, k in enumerate(keys):
        col = cols[0] if ci < 2 else cols[1]
        col.append(('<a class="toc-p"><span class="toc-no">%s</span><span class="toc-nm">%s</span>'
                    '<span class="toc-pg">%d</span></a>') % (PIAN[k]["no"], PIAN[k]["name"], pian_page[k]))
        for sec_no in sorted(pian_map[k].keys()):
            col.append(('<a class="toc-s"><span class="toc-st">%s</span>'
                        '<span class="toc-sg">%d</span></a>') % (esc(SECNAME[sec_no]), sec_page[(k, sec_no)]))
    inner = ('<div class="toc">'
             '<h2 class="pf-h">目录</h2><div class="pf-rule"></div>'
             '<div class="toc-cols"><div class="toc-col">%s</div><div class="toc-col">%s</div></div>'
             '<div class="toc-note">共 %d 条 · 4 篇 · 按「性价比」原序排列</div>'
             '</div>') % ("".join(cols[0]), "".join(cols[1]), len(SEL))
    return page_shell(inner, cls="pg-toc", page_no=2, hdr="目录")


def part(pian, page_no):
    d = PIAN[pian]
    n = sum(len(v) for v in pian_map[pian].values())
    g = defaultdict(int)
    for v in pian_map[pian].values():
        for e in v:
            g[GRADE(e["grade"])] += 1
    inner = ('<div class="pt">'
             '<div class="pt-no">%s</div>'
             '<h2 class="pt-t">%s</h2>'
             '<div class="pt-en">%s</div>'
             '<div class="pt-rule"></div>'
             '<p class="pt-lead">%s</p>'
             '<div class="pt-meta"><span><b>%d</b> 条</span>'
             '<span>证据 A <b>%d</b></span><span>B <b>%d</b></span><span>C <b>%d</b></span></div>'
             '</div>') % (d["no"], d["name"], d["en"], d["lead"], n, g["A"], g["B"], g["C"])
    return page_shell(inner, cls="pg-part", page_no=page_no, dark=True)


def entries(blocks, key, page_no):
    body = ""
    for b in blocks:
        if b["kind"] == "sec":
            body += sec_html(b["sec"])
        else:
            body += card_html(b["e"])
    return page_shell('<main class="ct">' + body + '</main>',
                      cls="pg-ent", page_no=page_no, hdr=KJCN[key])


def end():
    inner = (
        '<div class="pf">'
        '<h2 class="pf-h">来源与许可</h2><div class="pf-rule"></div>'
        '<p class="pf-lead">本册蒸馏自开源书籍《高性价比人生指南》，原著作者 '
        '<strong>eternity4719 及贡献者</strong>。</p>'
        '<table class="pf-tb pk">'
        '<tr><td class="g">原著</td><td>eternity4719/HowToLiveBetter（github.com/eternity4719/HowToLiveBetter）</td></tr>'
        '<tr><td class="g">许可</td><td>正文 CC BY 4.0（creativecommons.org/licenses/by/4.0/）；代码 MIT</td></tr>'
        '<tr><td class="g">本册</td><td><b>非官方</b>节选蒸馏版 · 仅节选「性价比极高」114 条并重排版式，文字内容未改写</td></tr>'
        '<tr><td class="g">时效</td><td>原书数据截至 2026-10 版本；法条、补贴标准与政策会更新，请以官方最新公布为准</td></tr>'
        '</table>'
        '<div class="pf-tip"><b>免责：</b>本册提供信息梳理，不代替诊断、处方、法律咨询等专业意见。'
        '遇到眼前的严重危险，请先求助。</div>'
        '<p class="pf-note">署名方式：转载或改编请保留「原著：高性价比人生指南（eternity4719/HowToLiveBetter）」'
        '与 CC BY 4.0 许可链接，并注明本册为节选蒸馏版本。</p>'
        '<div class="pf-stamp">由「蜂群」产线生成 · 2026-10-10</div>'
        '</div>'
    )
    return page_shell(inner, cls="pg-end", page_no=TOTAL, hdr="来源与许可")


# ---------- 组装 ----------
# 2026-10-10 第二轮：按主人要求删除「序 · 怎么用」（原 P2）与「来源与许可」（原 P43）。
#   preface() / end() 函数保留备查 —— 如需恢复，把它们加回 pages 并同步 TOTAL 与页码基准。
pages = [cover(), toc()]
n = 3
for p in body:
    if p["kind"] == "part":
        pages.append(part(p["pian"], n))
    else:
        pages.append(entries(p["blocks"], p["pian"], n))
    n += 1
assert len(pages) == TOTAL, "页数与 TOTAL 不一致：%d vs %d" % (len(pages), TOTAL)
# 末页显式打类，供 print 关掉 page-break-after（避免 PDF 多出一整页空白）
pages[-1] = pages[-1].replace('<section class="slide ', '<section class="slide last ', 1)

CSS = open(Path(__file__).with_name("theme_a4.css"), encoding="utf-8").read()

# ---------- 实测模式：渲染全部卡片，供浏览器量真实高度 ----------
if "--measure" in sys.argv:
    rows = []
    for key, secs in pian_map.items():
        for sec_no in sorted(secs.keys()):
            for e in secs[sec_no]:
                rows.append('<div class="mrow" data-k="%d:%d">%s</div>'
                            % (sec_no, e["idx"], card_html(e)))
    MHTML = ROOT / "01-工蜂产出" / "T3-版式" / "_measure.html"
    MHTML.write_text(
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><style>%s\n"
        ".mwrap{width:642px;margin:0;padding:0}\n.mrow{display:block}\n.mrow .cd{margin:0 !important}\n"
        "</style></head><body><div class=\"mwrap\">%s</div>"
        "<script>(function(){var o={};var rs=document.querySelectorAll('.mrow');"
        "for(var i=0;i<rs.length;i++){var c=rs[i].querySelector('.cd');"
        "o[rs[i].getAttribute('data-k')]=Math.round(c.getBoundingClientRect().height*100)/100;}"
        "var p=document.createElement('pre');p.textContent='@@'+'M'+'@@'+JSON.stringify(o)+'@@'+'M'+'@@';"
        "document.body.appendChild(p);})();</script></body></html>" % (CSS, "".join(rows)),
        encoding="utf-8")
    print("measure html written:", len(rows), "cards ->", MHTML)
    sys.exit(0)

ROUTER = """
<script>
(function(){
  var ss = document.querySelectorAll('.slide');
  function show(){
    var m = location.hash.match(/#\\/(\\d+)/);
    var i = m ? (parseInt(m[1],10)-1) : 0;
    for (var k=0;k<ss.length;k++){
      var on = (k===i);
      ss[k].className = ss[k].className.replace(/\\s*\\bon\\b/,'') + (on?' on':'');
      ss[k].style.display = on ? '' : 'none';
    }
  }
  window.addEventListener('hashchange', show);
  show();
})();
</script>
"""

doc = ("<!doctype html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\">\n"
       "<title>%s</title>\n<style>\n%s\n</style>\n</head>\n<body>\n%s\n%s\n</body>\n</html>\n"
       ) % (TITLE, CSS, "\n".join(pages), ROUTER)
OUT.write_text(doc, encoding="utf-8")
print("已写出:", OUT)
print("总页数:", TOTAL, "| 条目页:", sum(1 for p in body if p["kind"] == 'entries'),
      "| 篇扉:", sum(1 for p in body if p["kind"] == 'part'))
