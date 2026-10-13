# -*- coding: utf-8 -*-
"""T1 / W1 资料侦查蜂 —— 采集原著正文。
下载 eternity4719/HowToLiveBetter 的 book/ 全部正文 + README + 许可文件到 _源/。
"""
import json, time, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_源"
(SRC / "book").mkdir(parents=True, exist_ok=True)

REPO = "eternity4719/HowToLiveBetter"
UA = {"User-Agent": "Mozilla/5.0 (workbuddy-swarm; W1-scout)"}


def get(url, tries=5):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=50) as r:
                return r.read()
        except Exception as e:
            last = e
            print("  retry %d: %s" % (i + 1, e))
            time.sleep(2.0)
    print("  GIVE UP:", last)
    return None


def main():
    tree = get("https://api.github.com/repos/%s/git/trees/main?recursive=1" % REPO)
    if tree is None:
        raise SystemExit("目录树获取失败")
    d = json.loads(tree.decode("utf-8"))
    want = []
    for t in d["tree"]:
        if t.get("type") != "blob":
            continue
        p = t["path"]
        if p.startswith("book/") or p in ("README.md", "LICENSE", "LICENSE-CODE"):
            want.append(p)
    want.sort()
    print("待下载文件数:", len(want))

    ok, fail = 0, []
    for p in want:
        url = "https://raw.githubusercontent.com/%s/main/" % REPO + urllib.parse.quote(p)
        data = get(url)
        if data is None:
            fail.append(p)
            continue
        out = SRC / p
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        ok += 1
        print("  ok  %-46s %7d B" % (p, len(data)))

    print("完成 %d/%d" % (ok, len(want)))
    if fail:
        print("失败清单:")
        for f in fail:
            print("  -", f)
        raise SystemExit(1)


main()
