# -*- coding: utf-8 -*-
"""T1 / W1 资料侦查蜂 —— 原著正文结构化解析。
输入  : _源/book/*.md
输出  : 01-工蜂产出/T1-资料包-原著结构化数据集.json
        _work/parse_report.txt  (统计报告，用于人工核对口径)
"""
import json
import re
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "_源" / "book"
OUT_JSON = ROOT / "01-工蜂产出" / "T1-资料包-原著结构化数据集.json"
OUT_RPT = ROOT / "_work" / "parse_report.txt"

RE_SEC = re.compile(r"^#\s*(\d+)\.\s*(.+?)\s*$", re.M)
RE_ENT = re.compile(r"^###\s*(\d+)\.\s*(.+?)\s*$", re.M)
RE_TAG = re.compile(r"<!--\s*成本标签:\s*(.+?)\s*-->")
RE_FIELD = re.compile(r"^-\s*(成本|说人话|收益|证据等级|来源|备注)：\s*(.*)$")
FIELDS = ["成本", "说人话", "收益", "证据等级", "来源", "备注"]


def parse_tags(raw):
    """把 '钱=0 时间=少 毅力=些 收益=中 口径=金钱' 解析成 dict（不依赖固定顺序）。"""
    out = {}
    for kv in raw.split():
        if "=" in kv:
            k, v = kv.split("=", 1)
            out[k] = v
    return out


def parse_section(path):
    text = path.read_text(encoding="utf-8")
    m = RE_SEC.search(text)
    sec_no = int(m.group(1)) if m else None
    sec_name = m.group(2) if m else path.stem

    marks = list(RE_ENT.finditer(text))
    entries = []
    for i, mt in enumerate(marks):
        idx = int(mt.group(1))
        title = mt.group(2)
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        block = text[mt.end():end]

        tag_m = RE_TAG.search(block)
        tags = parse_tags(tag_m.group(1)) if tag_m else {}

        # 逐字段提取，支持续行（不以 '- ' / '#' / '<!--' 开头的行并入上一字段）
        fields = {f: "" for f in FIELDS}
        cur = None
        lines = []
        for ln in block.splitlines():
            s = ln.rstrip()
            fm = RE_FIELD.match(s)
            if fm:
                if cur:
                    fields[cur] = "\n".join(lines).strip()
                cur = fm.group(1)
                lines = [fm.group(2).strip()]
            elif cur is not None and s and not s.startswith(("- ", "#", "<!--", "|", ">", "[←")):
                lines.append(s.strip())
        if cur:
            fields[cur] = "\n".join(lines).strip()

        entries.append({
            "sec_no": sec_no,
            "sec_name": sec_name,
            "idx": idx,
            "title": title,
            "tags": tags,
            "cost": fields["成本"],
            "plain": fields["说人话"],
            "gain": fields["收益"],
            "grade": fields["证据等级"].strip(),
            "source": fields["来源"],
            "note": fields["备注"],
            "file": path.name,
            "has_tag": bool(tag_m),
        })
    return sec_no, sec_name, entries


def main():
    files = sorted(BOOK.glob("*.md"))
    sections, entries = [], []
    for f in files:
        sec_no, sec_name, ents = parse_section(f)
        sections.append({"sec_no": sec_no, "sec_name": sec_name,
                         "file": f.name, "entries": len(ents)})
        entries.extend(ents)

    data = OrderedDict([
        ("meta", {
            "source_repo": "eternity4719/HowToLiveBetter",
            "source_license": "CC BY 4.0 (正文) / MIT (代码)",
            "fetched_at": "2026-10-10",
            "sections": len(sections),
            "entries": len(entries),
        }),
        ("sections", sections),
        ("entries", entries),
    ])
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- 统计报告 ----
    L = []
    L.append("原著结构：%d 节 / %d 条" % (len(sections), len(entries)))
    L.append("")
    L.append("== 各节条目数 ==")
    for s in sections:
        L.append("  %2s  %-28s %3d" % (s["sec_no"], s["sec_name"], s["entries"]))

    L.append("")
    L.append("== 证据等级分布 ==")
    for k, v in Counter(e["grade"] for e in entries).most_common():
        L.append("  %-6s %4d" % (k, v))

    L.append("")
    L.append("== 标签缺失 ==")
    L.append("  无成本标签的条目: %d" % sum(1 for e in entries if not e["has_tag"]))

    for key in ["钱", "时间", "毅力", "收益", "口径"]:
        L.append("")
        L.append("== 标签 %s 取值分布 ==" % key)
        c = Counter(e["tags"].get(key, "<缺>") for e in entries)
        for k, v in c.most_common():
            L.append("  %-8s %4d" % (k, v))

    L.append("")
    L.append("== 候选『极高』口径试算 ==")

    def cnt(pred):
        return sum(1 for e in entries if pred(e))

    ZERO_MONEY = {"0"}
    ZERO_TIME = {"否", "0", "少"}      # 待验证
    ZERO_WILL = {"否", "0"}
    BIG = {"大"}

    r1 = cnt(lambda e: e["tags"].get("钱") in ZERO_MONEY and e["tags"].get("时间") in ZERO_TIME
             and e["tags"].get("毅力") in ZERO_WILL and e["tags"].get("收益") in BIG)
    r2 = cnt(lambda e: e["tags"].get("钱") in ZERO_MONEY and e["tags"].get("时间") in {"否", "0"}
             and e["tags"].get("毅力") in ZERO_WILL and e["tags"].get("收益") in BIG)
    L.append("  规则A(钱=0 & 时间∈{否,0,少} & 毅力∈{否,0} & 收益=大) = %d" % r1)
    L.append("  规则B(钱=0 & 时间∈{否,0}     & 毅力∈{否,0} & 收益=大) = %d" % r2)

    OUT_RPT.parent.mkdir(parents=True, exist_ok=True)
    OUT_RPT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print("\n已写出:", OUT_JSON.name)


main()
