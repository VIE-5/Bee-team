# -*- coding: utf-8 -*-
"""parse_source.py —— 从册子源 index.html 拆出「结构与板块」。

用途：`deck-*` 系列工具只看交付 PDF；本脚本补上「源侧」视角 ——
      页型家族（按结构性 class 数）、板块归属、逐页标题层、页脚内容类型。

用法：
    python parse_source.py <index.html> [--out <json>]

适配新册子：只改 SELECTORS 一张表（默认值对应土蚝 V6 / 碗香 的 DOM 约定）。
"""
import re, sys, json, html as H, argparse, collections
from pathlib import Path

# ── 结构性 class → 页型名（按需扩充） ─────────────────────────────
PAGE_KINDS = [
    ("cover", "封面"), ("end", "尾页"), ("section", "章节页"),
    ("bleed-clean", "满幅直出"), ("bleed-slide", "满幅直出"), ("bleed", "满幅直出"),
    ("", "物料页"),                       # 兜底：裸 .slide
]

# ── 结构件选择器 → 字段名（按需改写正则） ────────────────────────
SELECTORS = {
    "chap":   r'<div class="chap">(.*?)</div>',        # 页眉右：章节名（含序号）
    "sec_h":  r'<div class="sec-h">(.*?)</div>',       # 中文标题
    "sec_en": r'<div class="sec-en">(.*?)</div>',      # 英文副标
    "lead":   r'<div class="t-lead">(.*?)</div>',      # 大标题（可选）
    "badge":  r'<span class="badge">(.*?)</span>',     # 页脚左：内容类型
    "note":   r'<span class="note">(.*?)</span>',      # 页脚右：slogan
    "pg":     r'<div class="pg">(.*?)</div>',          # 页码
    "pill":   r'<div class="em-pill">(.*?)</div>',     # 章节页胶囊：板块名（无序号）
}
CN_NUM = "壹贰叁肆伍陆柒捌玖拾"


def kind_of(cls: str) -> str:
    for k, name in PAGE_KINDS:
        if k and k in cls:
            return name
    return "物料页"


def grab(chunk, pat):
    m = re.search(pat, chunk, re.S)
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""


def parse(html_text: str):
    pages = []
    for chunk in re.split(r'(?=<section class="slide)', html_text):
        m = re.match(r'<section class="slide([^"]*)">', chunk)
        if not m:
            continue
        cls = "slide" + m.group(1)
        # 页前注释 <!-- P04 · 品牌速览 -->
        pre = chunk[:chunk.find("<section")]
        cm = re.search(r'(P\d{1,2})\s*·\s*([^\n→]*?)\s*(?:═|-->|$)', pre)
        rec = {"cls": cls, "kind": kind_of(cls),
               "no": cm.group(1) if cm else "", "remark": cm.group(2).strip(" ═-") if cm else ""}
        for field, pat in SELECTORS.items():
            rec[field] = grab(chunk, pat)
        # 板块：拆出中文序号
        mm = re.match(r'([%s])(.*)' % CN_NUM, rec["chap"])
        rec["chap_num"], rec["chap_cn"] = (mm.group(1), mm.group(2).strip()) if mm else ("", rec["chap"])
        rec["n_img"] = len(re.findall(r'<img[^>]+src="([^"]+)"', chunk))
        rec["_chunk"] = chunk
        pages.append(rec)
    return pages


def report(pages):
    print("总页数 = %d" % len(pages))
    # ① 页型家族
    print("\n── 页型家族 ──")
    for k, v in collections.Counter(p["kind"] for p in pages).most_common():
        print("  %-8s %3d 页" % (k, v))
    assert sum(v for v in collections.Counter(p["kind"] for p in pages).values()) == len(pages), \
        "页型计数之和 != 总页数，class 判据需修正"
    # ② 板块聚合
    print("\n── 板块 ──")
    groups = collections.OrderedDict()
    for i, p in enumerate(pages, 1):
        key = (p["chap_num"] + p["chap_cn"]) if p["chap_num"] else "（导航/无章节标记）"
        groups.setdefault(key, []).append(i)
    for k, v in groups.items():
        contig = (v[-1] - v[0] + 1 == len(v))
        span = ("P%02d–P%02d" % (v[0], v[-1])) if contig else ("、".join("P%02d" % x for x in v))
        print("  %-16s %2d 页  %s" % (k, len(v), span))
    # ③ 逐页
    print("\n── 逐页 ──")
    for i, p in enumerate(pages, 1):
        sec = (p["chap_num"] + p["chap_cn"]) if p["chap_num"] else ""
        t = H.unescape(p["sec_h"] or p["remark"])
        en = H.unescape(p["sec_en"] or p["badge"])
        print("  P%02d [%-6s] %-12s %-22s %s  img=%d" % (i, p["kind"], sec, t, en, p["n_img"]))
    # ④ 自检：板块边界必须都有章节页
    print("\n── 自检 ──")
    print("  物料页缺任何板块标记:", [i + 1 for i, p in enumerate(pages)
                                if p["kind"] == "物料页" and not p["chap"] and not p["pill"]] or "无")
    # 每个板块的首页，其前一页应当是章节页（0-based: pages[f-2]）
    firsts = collections.OrderedDict()
    for i, p in enumerate(pages, 1):
        if p["chap_num"]:
            firsts.setdefault(p["chap_num"] + p["chap_cn"], i)
    orphan = []
    for name, f in firsts.items():
        prev = pages[f - 2] if f >= 2 else None
        if prev is None or prev["kind"] != "章节页":
            orphan.append("%s(P%02d，前一页 P%02d 是%s)" % (
                name, f, f - 1, prev["kind"] if prev else "无"))
    print("  板块缺章节页:", orphan or "无（全部边界都有章节页）")
    sec_pages = [p for p in pages if p["kind"] == "章节页"]
    print("  章节页 %d 张 / 板块 %d 个" % (len(sec_pages), len(firsts)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    txt = Path(a.html).read_text(encoding="utf-8")
    ps = parse(txt)
    report(ps)
    if a.out:
        Path(a.out).write_text(json.dumps(
            [{k: v for k, v in p.items() if k != "_chunk"} for p in ps],
            ensure_ascii=False, indent=1), encoding="utf-8")
        print("\n-> " + a.out)
