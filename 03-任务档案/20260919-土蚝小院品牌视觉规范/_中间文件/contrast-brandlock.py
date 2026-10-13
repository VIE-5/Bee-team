# -*- coding: utf-8 -*-
"""BrandLock v2 已定色板 —— 全对比度实算，为规范册重写提供数据。"""
import json
from pathlib import Path

OUT = Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉规范\_中间文件")

# BrandLock v2 §2 §3 已定色（唯一品牌事实源）
P = {
    "logo-ink":   ("#2D301B", "Logo 专用墨色（仅 Logo 内部）"),
    "logo-red":   ("#DE1C19", "Logo 印章红（标识内部色，不作色板色）"),
    "pine":       ("#58685A", "品牌主色 岭南松柏绿"),
    "rock":       ("#E7DCC7", "基底留白 暖米岩石色"),
    "walnut":     ("#76563C", "器物木料 深木胡桃色"),
    "darkblue":   ("#35464A", "深底夜色 黛青黑"),
    "cinnabar":   ("#A34435", "点睛色 朱砂红（物料统一红）"),
    "bronze":     ("#B28A52", "工艺金 铜金色"),
}

def lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def lum(h):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

def cr(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

rep = open(OUT / "contrast-brandlock.report.txt", "w", encoding="utf-8")
def W(*a):
    s = " ".join(str(x) for x in a); print(s); rep.write(s + "\n")

W("=== 各色相对亮度（决定一切搭配）")
for k, (h, d) in sorted(P.items(), key=lambda kv: -lum(kv[1][0])):
    W("  %-11s %s  L=%.4f   %s" % (k, h, lum(h), d))
W("")

grounds = ["rock", "pine", "darkblue", "walnut", "logo-ink"]
subjects = [("logo-ink", "Logo墨绿主体"), ("logo-red", "Logo朱印红"),
            ("cinnabar", "物料朱砂红"), ("bronze", "铜金"), ("walnut", "胡桃"),
            ("pine", "松柏绿")]

W("=== 底色 x 主体（>=3.0 可用 / 2.2-3.0 边缘 / <2.2 禁止）")
W("%-14s" % "底色" + "".join("  %-20s" % n for n, _ in subjects))
res = {}
for g in grounds:
    gh = P[g][0]
    row = "%-14s" % ("%s %s" % (g, gh))
    res[g] = {}
    for sk, sn in subjects:
        if P[sk][0] == gh:
            continue
        v = cr(P[sk][0], gh)
        verdict = "OK" if v >= 3.0 else ("EDGE" if v >= 2.2 else "NO")
        res[g][sk] = {"ratio": round(v, 2), "verdict": verdict}
        row += "  %-20s" % ("%.2f %s" % (v, verdict))
    W(row)
W("")

# 反白稿：主体 -> 暖米岩石色，朱印保留
W("=== 标志反白稿（主体转岩石米 #E7DCC7）落在各底")
for g in grounds:
    gh = P[g][0]
    v1 = cr("#E7DCC7", gh)
    v2 = cr("#DE1C19", gh)
    W("  on %-9s %s   主体 %.2f:1 %s   朱印 %.2f:1 %s"
      % (g, gh, v1, "OK" if v1 >= 3 else ("EDGE" if v1 >= 2.2 else "NO"),
         v2, "OK" if v2 >= 3 else ("EDGE" if v2 >= 2.2 else "NO")))
W("")
W("=== 关键结论")
W("  松柏绿(主色) 作标志承底 -> 墨绿主体 %.2f:1 / 朱印 %.2f:1"
  % (cr("#2D301B", "#58685A"), cr("#DE1C19", "#58685A")))
W("  黛青黑(深底) 作标志承底 -> 墨绿主体 %.2f:1 / 朱印 %.2f:1"
  % (cr("#2D301B", "#35464A"), cr("#DE1C19", "#35464A")))
W("  岩石米(基底) 作标志承底 -> 墨绿主体 %.2f:1 / 朱印 %.2f:1"
  % (cr("#2D301B", "#E7DCC7"), cr("#DE1C19", "#E7DCC7")))
W("  朱砂红 vs 松柏绿 %.2f:1 / vs 岩石米 %.2f:1 / vs 黛青黑 %.2f:1"
  % (cr("#A34435", "#58685A"), cr("#A34435", "#E7DCC7"), cr("#A34435", "#35464A")))
(OUT / "contrast-brandlock.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
rep.close()
