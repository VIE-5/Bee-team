# -*- coding: utf-8 -*-
"""对比 scale=1 / scale=2 两版 PDF 的体积与清晰度取舍。"""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
PROFILE = Path.home() / "_chrome_deck_profile"


def build(html, out, scale):
    if out.exists():
        out.unlink()
    with open(os.devnull, "wb") as nul:
        subprocess.run([
            str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
            "--no-pdf-header-footer",
            f"--force-device-scale-factor={scale}",
            f"--user-data-dir={PROFILE}",
            "--virtual-time-budget=40000",
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={out}",
            f"{html.as_uri()}?v={int(time.time()*1000)}",
        ], stdout=nul, stderr=nul)
    data = out.read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
    # 判是否含矢量文字：PDF 里字体对象
    fonts = len(re.findall(rb"/Type\s*/Font", data))
    imgs = len(re.findall(rb"/Subtype\s*/Image", data))
    print(f"scale={scale}  {out.stat().st_size/1024/1024:7.1f} MB  pages={pages}  "
          f"字体对象={fonts}  图像对象={imgs}")


if __name__ == "__main__":
    html = Path(sys.argv[1]).resolve()
    d = html.parent / "_pdfcmp"
    d.mkdir(exist_ok=True)
    build(html, d / "s1.pdf", 1)
    build(html, d / "s2.pdf", 2)
