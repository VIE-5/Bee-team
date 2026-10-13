# -*- coding: utf-8 -*-
"""
verify-images.py —— 用 Chrome 读真实 DOM，核对每个 <img> 是否真的加载成功

为什么需要它：
  图片 404 时页面**不会报错**，截图里只是碎图占位符。
  若靠肉眼翻 37 页找问题，极易漏。本脚本直接问浏览器：
  `img.naturalWidth === 0` 即加载失败（含路径错、格式不支持）。

用法：
    python verify-images.py <index.html>
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
PROFILE = Path.home() / "_chrome_deck_profile"

PROBE = """<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>
<script>
window.addEventListener('load', function(){
  var out = [];
  var imgs = document.querySelectorAll('img');
  for (var i=0;i<imgs.length;i++){
    var im = imgs[i];
    out.push({
      src: im.getAttribute('src'),
      ok: im.complete && im.naturalWidth > 0,
      nw: im.naturalWidth,
      nh: im.naturalHeight,
      dw: Math.round(im.getBoundingClientRect().width),
      dh: Math.round(im.getBoundingClientRect().height)
    });
  }
  document.title = 'PROBE:' + JSON.stringify(out);
});
</script>
</body></html>"""


def main():
    src = Path(sys.argv[1]).resolve()
    html = src.read_text(encoding="utf-8")

    # 收集页内所有 img src，改写为绝对 URI（模拟渲染时的解析）
    assets_uri = (src.parent / "assets").resolve().as_uri()
    srcs = re.findall(r'<img[^>]*\ssrc="([^"]+)"', html)
    resolved = []
    for s in srcs:
        if s.startswith("assets/"):
            resolved.append(f"{assets_uri}/{s[len('assets/'):]}")
        else:
            resolved.append(s)

    print(f"页内 <img> 共 {len(resolved)} 处，去重 {len(set(resolved))} 个")

    # 独立探针页：一次性把所有图挂上去，等 load 完读 naturalWidth
    probe = Path(tempfile.gettempdir()) / "_probe_imgs.html"
    imgs_html = "".join(f'<img src="{u}">' for u in sorted(set(resolved)))
    probe.write_text(
        f'<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>{imgs_html}'
        f'<script>window.addEventListener("load",function(){{'
        f'var o=[];document.querySelectorAll("img").forEach(function(im){{'
        f'o.push([im.getAttribute("src"),im.naturalWidth,im.naturalHeight]);}});'
        f'document.title="R:"+JSON.stringify(o);}});</script></body></html>',
        encoding="utf-8")

    # 用 --dump-dom 拿不到 title → 改用截图无关的办法：写结果到 DOM 再 dump
    with open(os.devnull, "wb") as nul:
        r = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu",
                            "--no-sandbox", "--virtual-time-budget=8000",
                            "--force-device-scale-factor=1",
                            f"--user-data-dir={PROFILE}",
                            "--dump-dom", probe.as_uri()],
                           stdout=subprocess.PIPE, stderr=nul)
    dom = r.stdout.decode("utf-8", "ignore")

    # --dump-dom 时 title 已写好
    m = re.search(r"<title>R:(.*?)</title>", dom, re.S)
    if not m:
        print("[!] 未能从 DOM 读到结果，回退：用文件系统核对存在性")
        bad = [u for u in sorted(set(resolved))
               if not Path(u.replace("file:///", "").replace("/", os.sep)).exists()]
        for b in bad:
            print("  [X] 缺失:", b)
        print(f"缺失 {len(bad)} 个" if bad else "[OK] 文件都在")
        return

    data = json.loads(m.group(1).replace("&quot;", '"'))
    bad = [(u, w, h) for u, w, h in data if not w or not h]
    for u, w, h in data:
        tag = "OK " if (w and h) else "[X]"
        print(f"  {tag} {w}x{h}  {u.split('/')[-1]}")
    print("-" * 56)
    if bad:
        print(f"[FAIL] {len(bad)} 张图未能加载：")
        for u, _, _ in bad:
            print("   ", u)
        sys.exit(1)
    print(f"[OK] 全部 {len(data)} 张图加载成功")


if __name__ == "__main__":
    main()
