# -*- coding: utf-8 -*-
"""T2 / W2 提案筑巢蜂 —— 蒸馏筛选。
按书籍自评口径提取『性价比极高』条目（钱=0 且 时间=少 且 毅力=否 且 收益=大）。
输出 : 01-工蜂产出/T2-蒸馏稿-极高性价比精选.md
       _work/distill_report.txt
"""
import json
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "01-工蜂产出" / "T1-资料包-原著结构化数据集.json").read_text(encoding="utf-8"))
OUT_MD = ROOT / "01-工蜂产出" / "T2-蒸馏稿-极高性价比精选.md"
OUT_RPT = ROOT / "_work" / "distill_report.txt"

entries = DATA["entries"]
sections = DATA["sections"]


def is_top(e):
    t = e["tags"]
    return (t.get("钱") == "0" and t.get("时间") == "少"
            and t.get("毅力") == "否" and t.get("收益") == "大")


top = [e for e in entries if is_top(e)]

# 口径归一（用于分组）
KJ = {"金钱": "金钱", "死亡率": "健康与寿命", "自由": "人身自由", "时间": "时间与精力"}
GRADE = lambda g: g.split("（")[0]

# ---- 报告 ----
L = []
L.append("蒸馏口径：钱=0 & 时间=少 & 毅力=否 & 收益=大  →  %d 条" % len(top))
L.append("")
L.append("== 极高条目在各节分布 ==")
per = OrderedDict((s["sec_no"], 0) for s in sections)
for e in top:
    per[e["sec_no"]] += 1
for s in sections:
    n = per[s["sec_no"]]
    bar = "#" * n
    L.append("  %2d %-26s %2d %s" % (s["sec_no"], s["sec_name"], n, bar))
empty = [s for s in sections if per[s["sec_no"]] == 0]
L.append("")
L.append("零极高条目的节：%s" % (", ".join("%d.%s" % (s["sec_no"], s["sec_name"]) for s in empty) or "无"))
L.append("")
L.append("== 按口径分组 ==")
bykj = {}
for e in top:
    bykj.setdefault(KJ.get(e["tags"].get("口径"), e["tags"].get("口径")), []).append(e)
for k, v in bykj.items():
    L.append("  %-10s %3d" % (k, len(v)))
OUT_RPT.write_text("\n".join(L), encoding="utf-8")
print("\n".join(L))

# ---- 蒸馏稿 Markdown ----
md = []
md.append("# 高性价比人生指南 · 极高性价比精选（蒸馏版）")
md.append("")
md.append("> 蒸馏自《高性价比人生指南》（eternity4719/HowToLiveBetter，CC BY 4.0）。")
md.append("> 口径：**不花钱（钱=0）· 不占时间（时间=少）· 不需要毅力（毅力=否）· 收益为大**，")
md.append("> 即原书 676 条中性价比「极高」的一档，共 %d 条。" % len(top))
md.append("")
for s in sections:
    lay = [e for e in top if e["sec_no"] == s["sec_no"]]
    if not lay:
        continue
    md.append("## %d. %s" % (s["sec_no"], s["sec_name"]))
    md.append("")
    for e in lay:
        md.append("### %s" % e["title"])
        md.append("- **说人话**：%s" % e["plain"].replace("\n", " "))
        md.append("- 成本：%s" % e["cost"].replace("\n", " "))
        md.append("- 证据等级：%s ｜ 换回：%s" % (GRADE(e["grade"]), e["tags"].get("口径")))
        md.append("- 来源：%s" % e["source"].replace("\n", " "))
        md.append("")
OUT_MD.write_text("\n".join(md), encoding="utf-8")
print("\n已写出:", OUT_MD.name, "|", OUT_RPT.name)
