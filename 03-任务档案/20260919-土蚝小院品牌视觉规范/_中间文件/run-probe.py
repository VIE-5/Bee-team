# -*- coding: utf-8 -*-
"""
run-probe.py —— 把 _probe.js 注入 index.html，用 Chrome headless --dump-dom 取回探针结果。

为什么这么做：deck 有 transform:scale 视口适配，截图只能看出"像不像"，
真正判几何（溢出 / 落位 / 宽高比）必须读运行时 getBoundingClientRect()。

坑：
  1. Chrome 必须带 --user-data-dir（纯 ASCII 临时目录），否则静默零产出
  2. 路径走 Path.as_uri()，中文 + 破折号路径才不被编码错
  3. PROBEOUT 在 dump 出来的 DOM 里是 HTML 转义状态，要反转义
"""
import html as htmlmod
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉规范\01-工蜂产出")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

src = (BASE / "index.html").read_text(encoding="utf-8")
probe = (BASE / "_probe.js").read_text(encoding="utf-8")

injected = src.replace("</body>", "<script>\n" + probe + "\n</script>\n</body>", 1)
if injected == src:
    print("ERROR: </body> not found, injection failed")
    sys.exit(1)

probe_html = BASE / "_probe.html"
probe_html.write_text(injected, encoding="utf-8")

ud = Path(tempfile.gettempdir()) / "tuhao_probe_ud"
ud.mkdir(parents=True, exist_ok=True)

cmd = [
    CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
    "--user-data-dir=" + str(ud),
    "--force-device-scale-factor=1",
    "--window-size=1920,1080",
    "--virtual-time-budget=8000",
    "--dump-dom",
    probe_html.as_uri(),
]
r = subprocess.run(cmd, capture_output=True, timeout=180)
dom = r.stdout.decode("utf-8", "replace")
(BASE / "_probe-dom.txt").write_text(dom, encoding="utf-8")

m = re.search(r'<div id="PROBEOUT"[^>]*>(.*?)</div>', dom, re.S)
if not m:
    (BASE / "_probe-report.txt").write_text(
        "PROBEOUT NOT FOUND. dom bytes=%d\n" % len(dom), encoding="utf-8")
    print("PROBEOUT NOT FOUND, dom bytes=%d" % len(dom))
    sys.exit(1)

txt = htmlmod.unescape(m.group(1)).strip()
(BASE / "_probe-report.txt").write_text(txt + "\n", encoding="utf-8")
print("probe report bytes=%d, dom bytes=%d" % (len(txt), len(dom)))
