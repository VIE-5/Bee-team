# -*- coding: utf-8 -*-
"""
render-one.py —— 逐页高清截图器（不依赖 runtime.js / 哈希导航）· v2

背景：render-deck.py 用 `<uri>#/<N>` 让 Chrome 跳到第 N 页，
      这要求 deck 自带 runtime.js 监听 hashchange 做翻页定位。
      本册是「多张固定尺寸 .slide 纵向平铺」结构（母版规格），
      **没有 runtime.js** → hash 被忽略 → 37 张截图全是同一屏（14:46 实测：
      37 个文件同一 md5）。

做法：给每页生成一个临时 HTML，只保留该页 .slide，直接量体截图。

⚠️ 踩坑①（2026-09-21）：临时页放在 `_pages/` 子目录，若只把 <link href> 改成
   `../assets/theme.css`、却忘记把 <img src="assets/..."> 也改写，
   图片会去 `_pages/assets/...` 找 → 全部 404 → 截图里全是碎图占位符，
   而 CSS/文字/页眉页脚完全正常 —— 极易被当成"只是图没加载"而漏过。
   本脚本把**所有** assets/ 引用统一换成绝对 file:// URI，一次性除根。

⚠️ 踩坑②（2026-09-21 高清要求）：主人要求「文字要清晰，图片要高清」。
   1× 截图在 PDF 里等价于 96dpi，小字号（11.5–13px）与图片会发虚。
   故改为 **--force-device-scale-factor=2** → 输出 2720×1700（等效 192dpi），
   配合素材长边 2720 的高清重制，文字与图片同时锐利。
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
SCALE = 2                       # ★ 高清倍率（主人 2026-09-21 要求）

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
    outdir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src.parent / "png"
    # 可选：--only 5,27,29,34 —— 只渲染指定页（调试/定点核对用）
    only = None
    for a in sys.argv[3:]:
        if a.startswith("--only"):
            spec = a.split("=", 1)[1] if "=" in a else sys.argv[sys.argv.index(a) + 1]
            only = {int(x) for x in spec.split(",") if x.strip().isdigit()}
    outdir.mkdir(parents=True, exist_ok=True)
    tmpdir = src.parent / "_pages"
    tmpdir.mkdir(exist_ok=True)

    html = src.read_text(encoding="utf-8")
    slides = re.findall(r'<section class="slide.*?</section>', html, re.S)
    print(f"发现 {len(slides)} 个 .slide" + (f"，只渲染 {sorted(only)}" if only else ""))

    assets_dir = src.parent / "assets"
    assets_uri = assets_dir.resolve().as_uri()
    css = f"{assets_uri}/theme.css"

    def absolutize(markup: str) -> str:
        return markup.replace('src="assets/', f'src="{assets_uri}/') \
                     .replace("src='assets/", f"src='{assets_uri}/")

    with open(os.devnull, "wb") as nul:
        for i, s in enumerate(slides, 1):
            if only and i not in only:
                continue
            page = tmpdir / f"p{i:02d}.html"
            page.write_text(TMPL.format(css=css, slide=absolutize(s)), encoding="utf-8")
            dst = outdir / f"slide-{i}.png"
            if dst.exists():
                dst.unlink()
            cmd = [str(CHROME), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                   "--no-sandbox", "--disable-application-cache",
                   f"--force-device-scale-factor={SCALE}",
                   f"--user-data-dir={PROFILE}",
                   "--virtual-time-budget=10000",
                   f"--window-size={PW},{PH}",
                   f"--screenshot={dst}",
                   f"{page.as_uri()}?v={int(time.time()*1000)}"]
            subprocess.run(cmd, stdout=nul, stderr=nul)
            kb = dst.stat().st_size / 1024 if dst.exists() else 0
            print(f"  [{i:2d}] {'OK  ' if kb > 0 else 'FAIL'} {kb:9.1f} KB")

    # —— 产物核对（R: 退出码 0 ≠ 成功）——
    files = sorted(outdir.glob("slide-*.png"))
    expect = len(only) if only else len(slides)
    print("-" * 52)
    print(f"产出 {len(files)}/{len(slides)} 张  (scale={SCALE}x, {PW*SCALE}x{PH*SCALE})  本次应有 {expect}" if not only
          else f"本次渲染 {expect} 张  (scale={SCALE}x, {PW*SCALE}x{PH*SCALE})")

    h = {}
    for f in files:
        d = hashlib.md5(f.read_bytes()).hexdigest()
        h.setdefault(d, []).append(f.name)
    dupes = {k: v for k, v in h.items() if len(v) > 1}
    print(f"唯一内容数：{len(h)} / {len(files)}")
    if dupes:
        print("[X] 存在重复页（渲染被冻结）：")
        for k, v in list(dupes.items())[:5]:
            print("   ", v)
    else:
        print("[OK] 全部页面内容唯一")


if __name__ == "__main__":
    main()
