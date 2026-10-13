# -*- coding: utf-8 -*-
"""字段长度分析 —— 为版式容量定参数。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "01-工蜂产出" / "T1-资料包-原著结构化数据集.json").read_text(encoding="utf-8"))
E = D["entries"]


def top(e):
    t = e["tags"]
    return t.get("钱") == "0" and t.get("时间") == "少" and t.get("毅力") == "否" and t.get("收益") == "大"


S = [e for e in E if top(e)]
ALL = E

def stat(name, xs):
    xs = sorted(len(x) for x in xs)
    n = len(xs)
    q = lambda p: xs[min(n - 1, int(n * p))]
    print("  %-10s n=%3d  中位%3d  均值%3d  P10%3d  P90%3d  最大%4d" %
          (name, n, q(.5), sum(xs) // n, q(.1), q(.9), xs[-1]))

print("== 全集 676 条 ==")
for f in ["title", "plain", "gain", "cost", "note", "source"]:
    stat(f, [e[f] for e in ALL])
print("== 精选 114 条 ==")
for f in ["title", "plain", "gain", "cost", "note", "source"]:
    stat(f, [e[f] for e in S])
print("== 精选 114 条 来源样例（前 6 条）==")
for e in S[:6]:
    print("  -", e["source"][:110])
print("== 来源中含多行的条数 ==", sum(1 for e in S if "\n" in e["source"]))
print("== 备注缺失条数 ==", sum(1 for e in S if not e["note"]))
print("== 说人话缺失条数 ==", sum(1 for e in S if not e["plain"]))
