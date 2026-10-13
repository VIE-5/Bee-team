# -*- coding: utf-8 -*-
"""跑 Chrome 量卡片真实高度 -> _work/card_heights.json
（铁律：分页预算不许估值，必须实测。）"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MHTML = ROOT / "01-工蜂产出" / "T3-版式" / "_measure.html"
OUT = ROOT / "_work" / "card_heights.json"
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
       "--user-data-dir=" + str(ROOT / "_work" / "chrome-measure"),
       "--force-device-scale-factor=1", "--window-size=1200,1000",
       "--virtual-time-budget=8000", "--dump-dom", MHTML.as_uri()]
res = subprocess.run(cmd, capture_output=True)
dom = res.stdout.decode("utf-8", "replace")
m = re.search(r"@@M@@(.*?)@@M@@", dom, re.S)
if not m:
    raise SystemExit("!! 探针未回传（检查 Chrome 路径与页面加载）")

data = json.loads(m.group(1))
OUT.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
vals = sorted(data.values())
print("卡片数:", len(data))
print("高度 min/中位/max: %.1f / %.1f / %.1f" % (vals[0], vals[len(vals) // 2], vals[-1]))
print("已写出:", OUT)
