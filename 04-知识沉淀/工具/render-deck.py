# -*- coding: utf-8 -*-
"""
render-deck.py —— html-ppt deck 的渲染 / 导出 / 验收一体脚本（Windows）

替代 render-win.bat —— 后者用 .bat + cmd，中文路径下易出编码问题。
本脚本全程 pathlib + Path.as_uri()，UTF-8 安全，且**强制做产物核对**。

用法：
    # 出 PNG（自动探页数，逐张截图 + 体检）
    python render-deck.py <index.html>

    # 只出指定页
    python render-deck.py <index.html> --pages 4,26,27

    # 导出 PDF
    python render-deck.py <index.html> --pdf

    # 出 PNG + PDF 一条龙
    python render-deck.py <index.html> --all

    # 拼联系表（一屏通读验收，强烈推荐）
    python render-deck.py <index.html> --sheet

    # 非 16:9 的册子（如 VI 母版 16:10）：视口给足画布尺寸，比例同步改
    python render-deck.py <index.html> --all --sheet --viewport 1360,850 --ratio 1.6

    # PDF 直接落交付名（免手工改名导致「交付件版本错位」）
    python render-deck.py <index.html> --all --pdfname "碗香-品牌全案封装.pdf"

    # 仅体检已有截图
    python render-deck.py <index.html> --check

设计要点（都是踩坑换来的）：
  1. **必须带 --user-data-dir**，否则 Chrome headless 静默零产出（退出码仍 0）
  2. **路径走 as_uri()**，中文/破折号路径才不会被编码错
  3. **URL 必须加时间戳破缓存**，否则改完 CSS 重渲染，截图还是旧样式 ——
     而且"退出码 0 + 文件确实生成了"，你只会以为改动没写对
  4. 跑完必核对产物：总数 / 体积分布 / 异常小文件告警
  5. 墨底满幅页 PNG 只 20–40KB 属正常，**小体积 ≠ 空白页**，
     真要判空白请用 --sheet 拼联系表肉眼看
  6. Chrome 的 stdout/stderr 用真 NUL 设备丢弃（Windows 上 subprocess.DEVNULL
     是 GetStdHandle，不是黑洞）
  7. **必须带 --force-device-scale-factor=1**。Windows 若开 DPI 缩放（常见
     125%/150%/175%），--window-size=1920,1080 实测只截出 1094×929 —— 验收图
     缩水看不清，deck 还会被额外缩放 0.86 倍
  8. **PDF 导出后必核「页数 == slide 数」**。若多出 1 页（末页近空白），
     说明有元素溢出 1080px 画布 —— 去 deck 的 @media print 里补
     `overflow:hidden !important`（screen 段里的 overflow 在 print 下不生效）
  9. **PDF 体积的唯一杠杆是「素材像素」，不是任何打印参数**。Chrome
     `--print-to-pdf` 用 `/FlateDecode`（无损）嵌入图片，且**不做降采样** ——
     素材多少像素就嵌多少像素。实测某册 47 个图像对象全是原始像素，
     stream 占 128.6MB（文件 99%）。
     → 出图前先按**显示尺寸**反推素材分辨率：
        显示 CSS 宽 W → PDF 占用 = W × 0.75 pt → 目标 dpi × (占用/72) inch = 所需 px
     例：图在页面占 521px 宽 → 391pt；素材 1920px 即 **353dpi（过剩 2.4 倍）**，
     1200px 是 **221dpi** 且体积降到 39%。别指望调 scale 或换编码（见要点 7 的
     `--force-device-scale-factor` 对 PDF 无效同源结论）。
 10. **视口必须与画布一致，否则截图带灰边**。本脚本原固定 `--window-size=1920,1080`，
     遇到 16:10（1360×850）的册子，画布只占中间一块、四周是 body 底色，
     截出来的就不是「满幅页面」。凡画幅非 16:9 → 用 `--viewport` 传画布尺寸，
     并配合 deck 主题的 `@media screen` 把 body 内边距/页间距归零并居中；
     视口 == 画布时截图即满幅、零灰边。（2026-09-27 碗香册实测）
 11. **MediaBox 比例别硬编码 16:9**：16:10 册子会被误报 `[!] 非16:9`。
     非 16:9 的册子用 `--ratio` 传目标比（如 1.6）。
 12. **PDF 名用 `--pdfname` 一次落成交付名**。默认出 `<deck名>.pdf`；
     若事后再手工改名，极易出现「PDF 比 index.html 旧」的交付件版本错位
     （2026-09-27 实测踩过：源已改编号，交付 PDF 还是旧版）。
"""
import argparse
import os
import re
import subprocess
import sys
import threading
import time
import traceback as _tb
from pathlib import Path

# ⚠️ Windows 控制台默认 GBK（cp936）。
# 别把 stdout 强行 reconfigure 成 utf-8 —— 那样 PowerShell 会按 GBK 解码 UTF-8
# 字节，中文全变乱码（'D:\WORK鈥斺€擵ie\...'，2026-09-18 实测）。
# 正确做法：保留系统编码（GBK 本来就支持中文），只把所有非 GBK 符号换成 ASCII
# （✓ ✗ ⚠ → [OK] [X] [!]），这样既不崩也不乱码。


def _install_quiet_thread_hook():
    """静默一种已知无害的噪音。

    现象：调 Chrome headless 时，Python 的某个 subprocess 读取线程会按系统 GBK
    去解码子进程输出，抛 UnicodeDecodeError，往 stderr 刷一屏 traceback。
    实测：与渲染结果无关（产物永远正确），但会掩盖真正的报错。
    所以只掐掉「来自 subprocess 的 UnicodeDecodeError」，其余异常照常暴露。
    """
    def hook(args):
        if args.exc_type is UnicodeDecodeError and args.exc_traceback is not None:
            files = [f.filename for f in _tb.extract_tb(args.exc_traceback)]
            if any("subprocess.py" in f for f in files):
                return
        threading.__excepthook__(args)
    threading.excepthook = hook


_install_quiet_thread_hook()

# ---------------- 常量 ----------------
CHROME_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe",
]
PROFILE = Path.home() / "_chrome_deck_profile"      # 纯 ASCII 临时 profile

# 体积参考线：低于此值需人工确认（但**不等于**空白）
SUSPICIOUS_KB = 12


def find_chrome() -> Path:
    for p in CHROME_CANDIDATES:
        if p.exists():
            return p
    sys.exit("[ERROR] 未找到 Chrome，请检查安装")


def count_slides(html: Path) -> int:
    """从 index.html 里数 .slide 个数（不依赖 runtime.js）"""
    txt = html.read_text(encoding="utf-8", errors="ignore")
    n = len(re.findall(r'class="[^"]*\bslide\b', txt))
    if n == 0:
        sys.exit("[ERROR] 没数到 .slide，确认这是 html-ppt 的 deck 吗？")
    return n


def run_chrome(chrome: Path, args: list[str]):
    cmd = [str(chrome), "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--no-sandbox", "--disable-application-cache",
           # ⚠️ 必须锁死设备像素比。Windows 若开了 DPI 缩放（常见 125%/150%/175%），
           # --window-size=1920,1080 会得到 1094×929 的视口、截图也跟着缩水，
           # 验收时看不清细节，还会让 deck 被 transform 缩到 0.86 倍。
           # 2026-09-18 实测：不加这条，截图只有 1094×929。
           "--force-device-scale-factor=1",
           f"--user-data-dir={PROFILE}"] + args
    # ⚠️ Windows 上 subprocess.DEVNULL 不是黑洞！它的实现是
    # GetStdHandle(STD_OUTPUT_HANDLE) —— 拿到的是 Python 从父进程继承来的
    # 管道句柄。Chrome 往那里写，数据就串回 PowerShell 管道，Python 的
    # _readerthread 再按系统 GBK 去解码 → UnicodeDecodeError 刷一屏。
    # （2026-09-18 实测：encoding="utf-8" 和 DEVNULL 都挡不住，只有显式打开
    #  NUL 设备才真正丢弃。）
    with open(os.devnull, "wb") as nul:
        return subprocess.run(cmd, stdout=nul, stderr=nul)


def cache_bust(uri: str) -> str:
    """给 URL 加时间戳，破 Chrome 缓存。
    不这么做的话：改了 CSS → 重渲染 → 截图仍是旧样式，
    且「退出码 0 + 文件确实生成了」，你只会以为改动没写对。
    2026-09-18 实测：格宽从 419.5 改 340 后重渲染，列数纹丝不动，就是这个坑。"""
    return f"{uri}?v={int(time.time() * 1000)}"


def render_png(chrome: Path, html: Path, outdir: Path, pages: list[int],
               viewport: str = "1920,1080") -> list[tuple[int, float]]:
    outdir.mkdir(parents=True, exist_ok=True)
    base = cache_bust(html.as_uri())
    results = []
    for i in pages:
        f = outdir / f"slide-{i}.png"
        if f.exists():
            f.unlink()
        run_chrome(chrome, [
            "--virtual-time-budget=6000",
            f"--window-size={viewport}",
            f"--screenshot={f}",
            f"{base}#/{i}",
        ])
        kb = f.stat().st_size / 1024 if f.exists() else 0.0
        results.append((i, kb))
        flag = "" if kb >= SUSPICIOUS_KB else "   <- [!] 体积偏小，请肉眼确认"
        status = "OK  " if kb > 0 else "FAIL"
        print(f"  [{i:2d}] {status} {kb:9.1f} KB{flag}")
    return results


def verify(results: list[tuple[int, float]], total: int):
    """产物核对 —— 绝不只看退出码"""
    print("-" * 56)
    got = [i for i, kb in results if kb > 0]
    fail = [i for i, kb in results if kb == 0]
    small = [i for i, kb in results if 0 < kb < SUSPICIOUS_KB]
    print(f"渲染成功 {len(got)}/{total}")
    if fail:
        print(f"  [X] 未生成页：{fail}")
    if small:
        print(f"  [!] 体积偏小页：{small}")
        print("    （墨底满幅页 20–40KB 属正常，请用 --sheet 拼联系表确认）")
    if not fail and not small:
        print("  [OK] 全部通过体积体检")
    return not fail


def export_pdf(chrome: Path, html: Path, out: Path, ratio: float = 16 / 9) -> bool:
    if out.exists():
        out.unlink()
    run_chrome(chrome, [
        "--no-pdf-header-footer",
        "--virtual-time-budget=20000",
        f"--print-to-pdf={out}",
        cache_bust(html.as_uri()),
    ])
    if not out.exists():
        print("[FAIL] PDF 未生成")
        return False
    # 核对页数与尺寸
    data = out.read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
    boxes = set(b.decode("ascii").strip() for b in re.findall(rb"/MediaBox\s*\[([^\]]+)\]", data))
    print(f"[OK] PDF: {out.name}  {out.stat().st_size/1024/1024:.1f} MB  页数={pages}")
    for b in boxes:
        v = [float(x) for x in b.split()]
        if len(v) == 4:
            w, h = v[2] - v[0], v[3] - v[1]
            r = w / h
            ratio_note = "  [OK]" if abs(r - ratio) < 0.01 else f"  [!] 非目标比例 ({r:.4f})"
            print(f"     MediaBox {w:g}x{h:g} pt{ratio_note}")
    return True


def make_sheet(outdir: Path, cols: int = 5, tw: int = 380) -> bool:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("[SKIP] 未安装 Pillow，跳联系表（pip install pillow）")
        return False
    files = sorted(outdir.glob("slide-*.png"),
                   key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)))
    if not files:
        print("[SKIP] 没有截图可拼")
        return False
    imgs = []
    for f in files:
        im = Image.open(f).convert("RGB")
        th = int(im.height * tw / im.width)
        imgs.append((re.search(r"(\d+)", f.stem).group(1),
                     im.resize((tw, th), Image.LANCZOS)))
    TH = imgs[0][1].height
    rows = (len(imgs) + cols - 1) // cols
    pad, lbl = 14, 26
    sheet = Image.new("RGB",
                      (cols * (tw + pad) + pad, rows * (TH + pad + lbl) + pad),
                      (248, 248, 248))
    d = ImageDraw.Draw(sheet)
    for idx, (name, im) in enumerate(imgs):
        r, c = divmod(idx, cols)
        x, y = pad + c * (tw + pad), pad + r * (TH + pad + lbl)
        sheet.paste(im, (x, y + lbl))
        d.text((x + 4, y + 6), f"P{int(name):02d}", fill=(15, 15, 15))
    out = outdir / "_contact-sheet.png"
    sheet.save(out, "PNG")
    print(f"[OK] 联系表: {out.name}  {sheet.size[0]}x{sheet.size[1]}  "
          f"{out.stat().st_size/1024:.0f} KB")
    return True


def main():
    ap = argparse.ArgumentParser(description="html-ppt deck 渲染 / 导出 / 验收")
    ap.add_argument("html", help="index.html 路径")
    ap.add_argument("--pages", help="逗号分隔的页码，如 4,26,27")
    ap.add_argument("--pdf", action="store_true", help="导出 PDF")
    ap.add_argument("--all", action="store_true", help="出 PNG + PDF")
    ap.add_argument("--sheet", action="store_true", help="拼联系表")
    ap.add_argument("--check", action="store_true", help="仅体检已有截图")
    ap.add_argument("--outdir", help="截图输出目录，默认 <deck>/png")
    ap.add_argument("--viewport", default="1920,1080",
                    help="截图视口 W,H，默认 1920,1080。画幅非 16:9 时请传画布尺寸"
                         "（如 16:10 的 VI 母版传 1360,850），否则截图带灰边")
    ap.add_argument("--ratio", type=float, default=16 / 9,
                    help="PDF MediaBox 目标宽高比，默认 1.7778（16:9）；16:10 传 1.6")
    ap.add_argument("--pdfname", help="PDF 输出名，默认 <deck名>.pdf；可传交付名，免手工改名")
    args = ap.parse_args()

    if not re.fullmatch(r"\d+,\d+", args.viewport):
        sys.exit(f"[ERROR] --viewport 须为 W,H 两个整数，收到: {args.viewport}")

    html = Path(args.html).resolve()
    if not html.exists():
        sys.exit(f"[ERROR] 文件不存在: {html}")

    outdir = Path(args.outdir) if args.outdir else html.parent / "png"
    base = html.stem

    chrome = find_chrome()
    total = count_slides(html)
    print(f"chrome  : {chrome}")
    print(f"deck    : {html}")
    print(f"slides  : {total} 页")
    print(f"outdir  : {outdir}")
    print(f"viewport: {args.viewport}")
    print("-" * 56)

    if args.check:
        # 仅体检（兼容 slide-N.png 与 <deck名>_N.png 两种命名）
        files = sorted(outdir.glob("slide-*.png")) or sorted(outdir.glob(f"{base}_*.png"))
        if not files:
            sys.exit("[ERROR] 没有找到截图")
        res = []
        for f in files:
            n = int(re.search(r"(\d+)", f.stem).group(1))
            res.append((n, f.stat().st_size / 1024))
        print(f"  发现 {len(res)} 张已有截图")
        verify(res, total)
        return

    need_render = not args.pdf or args.all
    if need_render:
        if args.pages:
            pages = [int(x) for x in args.pages.split(",")]
        else:
            pages = list(range(1, total + 1))
        # 用 base_ 前缀，与 bat 脚本产物命名兼容
        res = render_png(chrome, html, outdir, pages, args.viewport)
        if not verify(res, total if len(pages) == total else len(pages)):
            sys.exit("[FAIL] 有页面未生成，请检查")

    if args.pdf or args.all:
        pdf_out = Path(args.pdfname) if args.pdfname else Path(f"{base}.pdf")
        if not pdf_out.is_absolute():
            pdf_out = html.parent / pdf_out
        if not export_pdf(chrome, html, pdf_out, args.ratio):
            sys.exit("[FAIL] PDF 导出失败")

    if args.sheet:
        make_sheet(outdir)

    print("\n完成。")


if __name__ == "__main__":
    main()
