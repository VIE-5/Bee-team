# -*- coding: utf-8 -*-
"""五维对标汇总：读两份 .probe.json，输出可量化对比表。数字全部来自 PDF 实测。"""
import json, collections, statistics

A = json.load(open(r"E:/唐V-work/土蚝小院/土蚝小院-品牌视觉全案-v6.pdf.probe.json", encoding="utf-8"))
B = json.load(open(r"D:/WORK——Vie/贵州遵义/邓总-VI/沃克/品牌全案封装/01-工蜂产出/碗香-品牌全案封装.pdf.probe.json", encoding="utf-8"))

def rep(name, rows, size_mb):
    n = len(rows)
    with_hdr = sum(1 for r in rows if r["hdr"])
    with_ftr = sum(1 for r in rows if r["ftr"])
    zero_txt = sum(1 for r in rows if r["n_blocks"] == 0)
    one_img = sum(1 for r in rows if r["n_img"] == 1)
    multi_img = sum(1 for r in rows if r["n_img"] >= 5)
    full = sum(r["full_bleed"] for r in rows)
    chars = [r["n_txt_chars"] for r in rows]
    body_chars = [r["n_txt_chars"] for r in rows if r["n_blocks"] > 0]
    print("\n===== %s =====" % name)
    print("  页数            : %d" % n)
    print("  文件体积        : %.1f MB   单页均重 %.2f MB" % (size_mb, size_mb / n))
    print("  有页眉的页      : %d (%.0f%%)" % (with_hdr, with_hdr / n * 100))
    print("  有页脚的页      : %d (%.0f%%)" % (with_ftr, with_ftr / n * 100))
    print("  **正文零文本层页**: %d (%.0f%%)   <- 正文块数=0，文字全在像素里" % (zero_txt, zero_txt / n * 100))
    print("  单图页(1图)     : %d (%.0f%%)" % (one_img, one_img / n * 100))
    print("  多图页(>=5图)   : %d (%.0f%%)" % (multi_img, multi_img / n * 100))
    print("  满幅出血图层    : %d 处" % full)
    print("  每页字符数 中位 %.0f  均 %.0f  最大 %d" % (statistics.median(chars), statistics.mean(chars), max(chars)))
    if body_chars:
        print("  有正文页字符中位 %.0f   <- 真正承载说明文字的密度" % statistics.median(body_chars))
    # 页眉里出现过的章节词（粗判导航承载方式）
    parts = collections.Counter()
    for r in rows:
        for h in r["hdr"]:
            for kw in ["壹", "贰", "叁", "肆", "伍", "陆", "柒", "Ⅰ", "Ⅱ", "Ⅲ"]:
                if kw in h:
                    parts[kw] += 1
    print("  页眉承载章节标记: %s" % dict(parts) if parts else "  页眉承载章节标记: 无")
    return dict(n=n, zero_txt=zero_txt, size_mb=size_mb)

a = rep("土蚝小院 V6（60 页）", A, 95146715 / 1024 / 1024)
b = rep("碗香（55 页）", B, 101104606 / 1024 / 1024)
print("\n===== 关键落差 =====")
print("  零文本层页占比   : V6 %.0f%%  vs  碗香 %.0f%%" % (a["zero_txt"] / a["n"] * 100, b["zero_txt"] / b["n"] * 100))
print("  单页均重         : V6 %.2f MB  vs  碗香 %.2f MB  (%.2fx)" % (a["size_mb"] / a["n"], b["size_mb"] / b["n"], (b["size_mb"] / b["n"]) / (a["size_mb"] / a["n"])))
