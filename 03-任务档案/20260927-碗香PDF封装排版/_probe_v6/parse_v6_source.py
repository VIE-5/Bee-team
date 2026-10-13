# -*- coding: utf-8 -*-
"""V6 结构与板块拆解：从源 index.html 抽每页的 页型 / 板块 / 标题 / 页脚内容类型。"""
import re, pathlib, json

SRC = pathlib.Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案"
                   r"\20260921-土蚝小院品牌全案封装\01-工蜂产出\index.html")
html = SRC.read_text(encoding="utf-8")

# 按 <section class="slide..."> ... </section> 切页
parts = re.split(r'(?=<section class="slide)', html)
pages = []
for chunk in parts:
    m = re.match(r'<section class="slide([^"]*)">', chunk)
    if not m:
        continue
    cls = ("slide" + m.group(1)).strip()
    # 页前注释：P04 · 品牌速览
    pre = chunk[:chunk.find("<section")]
    cm = re.search(r'(P\d{1,2}) · ([^\n]*?)\s*(?:═|-->|$)', pre)
    tag_no = cm.group(1) if cm else ""
    remark = cm.group(2).strip(" ═-") if cm else ""

    def grab(pat, default=""):
        g = re.search(pat, chunk, re.S)
        return re.sub(r"<[^>]+>", "", g.group(1)).strip() if g else default

    chap = grab(r'<div class="chap">(.*?)</div>')
    chap_num = ""
    cn = ""
    mm = re.match(r'([壹贰叁肆伍陆柒捌玖])(.*)', chap)
    if mm:
        chap_num, cn = mm.group(1), mm.group(2).strip()
    else:
        cn = chap
    sec_h = grab(r'<div class="sec-h">(.*?)</div>')
    sec_en = grab(r'<div class="sec-en">(.*?)</div>')
    badge = grab(r'<span class="badge">(.*?)</span>')
    note = grab(r'<span class="note">(.*?)</span>')
    big = grab(r'<div class="t-lead">(.*?)</div>') or grab(r'<div class="lead">(.*?)</div>')
    pg_no = grab(r'<div class="pg">(.*?)</div>')
    imgs = re.findall(r'<img[^>]+src="([^"]+)"', chunk)

    pages.append(dict(cls=cls, no=tag_no, remark=remark, chap=cn, chap_num=chap_num,
                      sec_h=sec_h, sec_en=sec_en, badge=badge, note=note,
                      lead=big, pg=pg_no, n_img=len(imgs), imgs=imgs))

print("总页数 =", len(pages))
for i, p in enumerate(pages, 1):
    kind = p["cls"].replace("slide", "").strip() or "material"
    sec = (p["chap_num"] + p["chap"]) if p["chap_num"] else p["chap"]
    print("P%02d | %-14s | %-12s | %-22s | %s" % (
        i, kind, sec, p["sec_h"] or p["remark"][:14], p["sec_en"] or p["badge"]))

pathlib.Path("_v6_structure.json").write_text(
    json.dumps(pages, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n-> _v6_structure.json")
