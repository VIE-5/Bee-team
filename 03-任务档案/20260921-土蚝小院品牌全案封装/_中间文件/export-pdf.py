# -*- coding: utf-8 -*-
"""
export-pdf.py —— 高清 PDF 导出（v2 · 主人 2026-09-21 要求「文字清晰、图片高清」）

要点：
  1. `@page { size:1360px 850px; margin:0 }` 已在 theme.css 锁死 → 每页一张 slide。
  2. 加 `--force-device-scale-factor=2`：Chrome 打印 PDF 时按 2× 光栅化，
     等效 192dpi，小字号（11.5–13px）与图片在 PDF 里不再发虚。
  3. `--no-pdf-header-footer` 关掉浏览器自带的页眉页脚（否则多出 URL/日期）。
  4. 收尾核对：页数 == slide 数、MediaBox 尺寸、文件体积。
     ⚠️「退出码 0」≠「任务成功」—— 必须数页数。
"""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
PROFILE = Path.home() / "_chrome_deck_profile"


def main():
    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src.parent / "deck.pdf"
    expect_pages = int(sys.argv[3]) if len(sys.argv) > 3 else None

    if out.exists():
        out.unlink()

    with open(os.devnull, "wb") as nul:
        subprocess.run([
            str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
            "--no-pdf-header-footer",
            "--force-device-scale-factor=2",       # ★ 高清光栅化
            f"--user-data-dir={PROFILE}",
            "--virtual-time-budget=40000",         # 大图册给足加载时间
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={out}",
            f"{src.as_uri()}?v={int(time.time()*1000)}",
        ], stdout=nul, stderr=nul)

    if not out.exists():
        print("[FAIL] PDF 未生成")
        sys.exit(1)

    data = out.read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
    mb = out.stat().st_size / 1024 / 1024
    print(f"[OK] {out.name}  {mb:.1f} MB  页数={pages}")

    boxes = set(b.decode("ascii").strip() for b in re.findall(rb"/MediaBox\s*\[([^\]]+)\]", data))
    for b in boxes:
        v = [float(x) for x in b.split()]
        if len(v) == 4:
            w, h = v[2] - v[0], v[3] - v[1]
            print(f"     MediaBox {w:g}x{h:g} pt  (比例 {w/h:.4f})")

    if expect_pages is not None:
        if pages == expect_pages:
            print(f"     [OK] 页数 == slide 数 ({expect_pages})")
        else:
            print(f"     [X] 页数 {pages} != slide 数 {expect_pages} —— 有内容溢出多出页！")


if __name__ == "__main__":
    main()
