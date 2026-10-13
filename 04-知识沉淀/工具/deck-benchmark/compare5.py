# -*- coding: utf-8 -*-
"""五维对标汇总：读两份 .probe.json（由 probe_structure.py 生成），输出可量化对比表。

用法:
    python compare5.py <A.pdf> <B.pdf> [A标签] [B标签]
说明:
    两个 PDF 必须先用 probe_structure.py 跑过，生成同目录 .probe.json。
    数字全部来自 PDF 实测，不引用任何自述。
"""
import sys, json, collections, statistics

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(1)

PA, PB = sys.argv[1], sys.argv[2]
LA = sys.argv[3] if len(sys.argv) > 3 else "A"
LB = sys.argv[4] if len(sys.argv) > 4 else "B"


def load(path):
    with open(path + ".probe.json", encoding="utf-8") as f:
        return json.load(f)


def rep(name, rows, size_mb=0.0):
    n = len(rows)
    with_hdr = sum(1 for r in rows if r["hdr"])
    with_ftr = sum(1 for r in rows if r["ftr"])
    # 正确判据：正文块数 == 0（不是字符数 —— 页眉页脚也有几十字，会误导）
    zero_txt = sum(1 for r in rows if r["n_blocks"] == 0)
    one_img = sum(1 for r in rows if r["n_img"] == 1)
    multi_img = sum(1 for r in rows if r["n_img"] >= 5)
    full = sum(r["full_bleed"] for r in rows)
    chars = [r["n_txt_chars"] for r in rows]
    body_chars = [r["n_txt_chars"] for r in rows if r["n_blocks"] > 0]
    print("\n===== %s =====" % name)
    print("  页数              : %d" % n)
    if size_mb:
        print("  文件体积          : %.1f MB   单页均重 %.2f MB" % (size_mb, size_mb / n))
    print("  有页眉的页        : %d (%.0f%%)" % (with_hdr, with_hdr / n * 100))
    print("  有页脚的页        : %d (%.0f%%)" % (with_ftr, with_ftr / n * 100))
    print("  **正文零文本层页** : %d (%.0f%%)   <- 正文块数=0，文字全在像素里" % (zero_txt, zero_txt / n * 100))
    print("  单图页(1图)       : %d (%.0f%%)" % (one_img, one_img / n * 100))
    print("  多图页(>=5图)     : %d (%.0f%%)" % (multi_img, multi_img / n * 100))
    print("  满幅出血图层      : %d 处" % full)
    print("  每页字符数 中位 %.0f  均 %.0f  最大 %d" % (statistics.median(chars), statistics.mean(chars), max(chars)))
    if body_chars:
        print("  有正文页字符中位  %.0f   <- 真正承载说明文字的密度" % statistics.median(body_chars))
    parts = collections.Counter()
    for r in rows:
        for h in r["hdr"]:
            for kw in ["壹", "贰", "叁", "肆", "伍", "陆", "柒", "Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ"]:
                if kw in h:
                    parts[kw] += 1
    print("  页眉承载章节标记  : %s" % (dict(parts) if parts else "无"))
    return dict(n=n, zero_txt=zero_txt)


a = rep("%s" % LA, load(PA))
b = rep("%s" % LB, load(PB))
print("\n===== 关键落差 =====")
print("  正文零文本层页占比 : %s %.0f%%  vs  %s %.0f%%"
      % (LA, a["zero_txt"] / a["n"] * 100, LB, b["zero_txt"] / b["n"] * 100))
