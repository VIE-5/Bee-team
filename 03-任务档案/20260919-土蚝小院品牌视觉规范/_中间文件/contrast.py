# -*- coding: utf-8 -*-
"""WCAG contrast for every ground x logo-variant pair — the pairing matrix must be measured, not eyeballed."""
import json
from pathlib import Path

OUT = Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉规范\_中间文件")

C = {
    "ink":    "#2D301B", "seal": "#DF1D1A", "pine": "#58685A",
    "cream":  "#FDF4E3", "deep": "#1A1F0B", "paper": "#E9E0D3", "white": "#FFFFFF",
}

def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def lum(hexs):
    r, g, b = (int(hexs[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

def cr(a, b):
    la, lb = lum(C[a]), lum(C[b])
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

rep = open(OUT / "contrast.report.txt", "w", encoding="utf-8")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); rep.write(s + "\n")

grounds = ["cream", "white", "paper", "pine", "ink", "deep"]
subjects = [("正稿主体 墨绿", "ink"), ("反白主体 米白", "cream"), ("印章红", "seal")]

P("WCAG 对比度（>=3:1 视为标志可用下限，>=4.5:1 视为舒适）")
P("")
head = "%-14s" % "底色"
for n, _ in subjects:
    head += "  %-16s" % n
P(head)
res = {}
for g in grounds:
    row = "%-14s" % ("%s %s" % (g, C[g]))
    res[g] = {}
    for name, s in subjects:
        v = cr(s, g)
        verdict = "OK" if v >= 3.0 else ("EDGE" if v >= 2.2 else "NO")
        res[g][name] = {"ratio": round(v, 2), "verdict": verdict}
        row += "  %-16s" % ("%.2f:1  %s" % (v, verdict))
    P(row)
P("")
P("重点结论：")
P("  墨绿 vs 米白  = %.2f:1   <- 正稿/反白的主对比，扎实" % cr("ink", "cream"))
P("  墨绿 vs 松柏绿 = %.2f:1   <- 上版主色与本版主色不可叠加使用" % cr("ink", "pine"))
P("  印章红 vs 墨绿 = %.2f:1" % cr("seal", "ink"))
P("  印章红 vs 深墨绿 = %.2f:1" % cr("seal", "deep"))
P("  印章红 vs 松柏绿 = %.2f:1" % cr("seal", "pine"))
(OUT / "contrast.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
rep.close()
