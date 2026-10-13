# -*- coding: utf-8 -*-
"""render-range.py —— 只渲染指定页区间（续跑用）

⚠️ 临时页在 `_pages/` 下，所有 `assets/` 引用必须改写成绝对 file:// URI，
   否则图片全部 404（截图里只有碎图占位符，而 CSS/文字仍正常，极易漏检）。
"""
import hashlib
import os
import re
import subprocess
import sys
import time
from pathlib import Path

CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
PROFILE = Path.home() / "_chrome_deck_profile"
PW, PH = 1360, 850

TMPL = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<link rel="stylesheet" href="{css}">
<style>
  html,body{{background:#fff!important;margin:0!important;padding:0!important;gap:0!important;}}
  .slide{{box-shadow:none!important;margin:0!important;}}
</style>
</head><body>{slide}</body></html>"""


def main():
    src = Path(sys.argv[1]).resolve()
    outdir = Path(sys.argv[2]).resolve()
    lo, hi = int(sys.argv[3]), int(sys.argv[4])
    tmpdir = src.parent / "_pages"
    tmpdir.mkdir(exist_ok=True)
    outdir.mkdir(parents=True, exist_ok=True)

    html = src.read_text(encoding="utf-8")
    slides = re.findall(r'<section class="slide.*?</section>', html, re.S)
    print(f"总 {len(slides)} 页，渲染 {lo}..{hi}")

    assets_uri = (src.parent / "assets").resolve().as_uri()
    css = f"{assets_uri}/theme.css"

    def absolutize(m: str) -> str:
        return m.replace('src="assets/', f'src="{assets_uri}/')

    with open(os.devnull, "wb") as nul:
        for i in range(lo, hi + 1):
            page = tmpdir / f"p{i:02d}.html"
            page.write_text(TMPL.format(css=css, slide=absolutize(slides[i - 1])),
                            encoding="utf-8")
            dst = outdir / f"slide-{i}.png"
            if dst.exists():
                dst.unlink()
            subprocess.run([str(CHROME), "--headless=new", "--disable-gpu",
                            "--hide-scrollbars", "--no-sandbox",
                            "--disable-application-cache",
                            "--force-device-scale-factor=1",
                            f"--user-data-dir={PROFILE}",
                            "--virtual-time-budget=8000",
                            f"--window-size={PW},{PH}",
                            f"--screenshot={dst}",
                            f"{page.as_uri()}?v={int(time.time()*1000)}"],
                           stdout=nul, stderr=nul)
            kb = dst.stat().st_size / 1024 if dst.exists() else 0
            print(f"  [{i:2d}] {'OK  ' if kb > 0 else 'FAIL'} {kb:9.1f} KB")

    # 全量唯一性复核
    files = sorted(outdir.glob("slide-*.png"),
                   key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)))
    h = {}
    for f in files:
        h.setdefault(hashlib.md5(f.read_bytes()).hexdigest(), []).append(f.name)
    print("-" * 50)
    print(f"文件数 {len(files)}，唯一内容 {len(h)}")
    dupes = [v for v in h.values() if len(v) > 1]
    print("[X] 重复：" + str(dupes) if dupes else "[OK] 全部唯一")


if __name__ == "__main__":
    main()
