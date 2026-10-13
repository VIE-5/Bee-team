# -*- coding: utf-8 -*-
"""
标志方案展示 · 通用素材加工（母版）
================================================
输入：一个放着 N 版标志图的目录
输出：每版的「彩色去背 / 灰阶 / 单色墨 / 反白」四态（均已裁掉透明边）+ 真实用色聚类

用法：只改下面【配置区】，然后
    python prep-assets.py
产出落在 <WK>/assets/ 与 <WK>/assets/trim/

关键设计（踩过坑的地方，别改回去）：
1. 白底图用「四角洪水填充」去背，**不可**用全局白转透明
   —— 那会把白厨师服、牙齿、头巾一起吃掉。
2. 反白稿必须用「双色互换」：暗部 -> 白，亮部 -> 本版主色。
   **不可**把所有可见像素涂白 —— 那只会得到一坨无结构的纯白剪影。
3. 去背图生成后**必须裁透明边**（trim）。原图常自带大片透明边，
   直接等比缩放会导致内容只占框宽六成，多版并排时大小明显不一。
4. 裁边用 alpha 阈值 >12 求 bbox，而不是 getbbox() 的默认行为。
"""
import os
import json
from PIL import Image, ImageDraw, ImageOps

# ==================== 配置区（只改这里） ====================
SRC = r'D:\...\Logo\二'                    # 原始素材目录
WK = r'D:\...\Logo二-全案封装\_work'        # 工作目录
FILES = {                                   # key 将贯穿 build.py（A/B/C…，建议 ≤4 版）
    'A': '版1_红金复古国潮_透明.png',
    'B': '版2_深绿米黄乡土_透明.png',
    'C': 'ChatGPT Image 2026年9月18日 09_51_07.png',
}
PRIM = {                                    # 各版主色 RGB，供反白稿「亮部」着色（取自色值提取结果）
    'A': (0x8A, 0x0F, 0x0D),
    'B': (0x07, 0x43, 0x30),
    'C': (0xA8, 0x0F, 0x0D),
}
# ============================================================

OUT = os.path.join(WK, 'assets')
TRIM = os.path.join(OUT, 'trim')
os.makedirs(TRIM, exist_ok=True)


def strip_white(im, thresh=42):
    """四角洪水填充去白底（内部白色保留）"""
    work = im.convert('RGBA').copy()
    w, h = work.size
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(work, seed, (0, 0, 0, 0), thresh=thresh)
    return work


def alpha_cover(im):
    hist = im.getchannel('A').histogram()
    return hist[0] / sum(hist) * 100


def trim(im, name):
    al = im.getchannel('A').point(lambda v: 255 if v > 12 else 0)
    bb = al.getbbox()
    if bb is None:
        print(f'   {name:22s} EMPTY!')
        return None
    c = im.crop(bb)
    c.save(os.path.join(TRIM, name))
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    print(f'   {name:22s} {im.size} -> bbox {bb}  {w}x{h}  比例 {w/h:.3f}')
    return c


def palette(im, k):
    """非透明 + 非近白像素量化，取前 12 色（判读主色用）"""
    rgba = im.convert('RGBA')
    px = list(rgba.getdata())
    keep = [p[:3] for p in px
            if p[3] > 200 and not (p[0] > 232 and p[1] > 232 and p[2] > 232)]
    if not keep:
        print(f'   [{k}] 无有效像素'); return []
    tmp = Image.new('RGB', (len(keep), 1))
    tmp.putdata(keep)
    q = tmp.quantize(colors=16, method=Image.MEDIANCUT)
    pal = q.getpalette()
    rows = []
    print(f'   [{k}] 有效像素 {len(keep)/len(px)*100:.1f}%  ({len(keep)})')
    for cnt, idx in sorted(q.getcolors(), reverse=True)[:12]:
        r, g, b = pal[idx * 3: idx * 3 + 3]
        pct = cnt / len(keep) * 100
        rows.append([f'#{r:02X}{g:02X}{b:02X}', round(pct, 2)])
        print(f'        #{r:02X}{g:02X}{b:02X}  {pct:5.2f}%')
    return rows


report = {}
checks = []
for k, fn in FILES.items():
    im = Image.open(os.path.join(SRC, fn))
    print('=' * 64)
    print(f'[{k}] {fn}  {im.size}  {im.mode}')

    if im.mode != 'RGBA':
        print('   白底不透明 -> 洪水填充去背')
        im = strip_white(im)
    else:
        im = im.convert('RGBA')

    print(f'   透明占比 {alpha_cover(im):.1f}%')
    im.save(os.path.join(OUT, f'logo-{k}.png'))

    gray = ImageOps.grayscale(im.convert('RGB'))
    # 灰阶（保留 alpha）
    Image.merge('RGBA', (gray, gray, gray, im.getchannel('A'))).save(
        os.path.join(OUT, f'logo-{k}-gray.png'))
    # 单色墨稿（阈值二值）
    bw = gray.point(lambda v: 0 if v < 128 else 255)
    Image.merge('RGBA', (bw, bw, bw, im.getchannel('A'))).save(
        os.path.join(OUT, f'logo-{k}-mono.png'))
    # 反白稿：双色互换（暗部 -> 白，亮部 -> 本版主色）
    lum = gray.point(lambda v: 255 if v >= 128 else 0)
    rev = Image.composite(Image.new('RGB', im.size, PRIM[k]),
                          Image.new('RGB', im.size, (255, 255, 255)), lum)
    rev = rev.convert('RGBA'); rev.putalpha(im.getchannel('A'))
    rev.save(os.path.join(OUT, f'logo-{k}-reverse.png'))

    print('   裁透明边：')
    tr = {}
    for suf in ['', '-gray', '-mono', '-reverse']:
        n = f'logo-{k}{suf}.png'
        c = trim(Image.open(os.path.join(OUT, n)).convert('RGBA'), n)
        if c is not None:
            tr[suf] = c
    base = tr['']

    print('   真实用色：')
    report[k] = palette(base, k)

    # 核对图 3 格：彩色@白底 | 彩色@深底 | 反白@深底（查白边残留与反白结构）
    DARKBG = (29, 25, 26, 255)

    def fit(img, box=460):
        w, h = img.size
        s = min(1.0, box / max(w, h))
        return img.resize((int(w * s), int(h * s)), Image.LANCZOS)

    c1, c2 = fit(base), fit(tr['-reverse'])
    tw, th = max(c1.width, c2.width), max(c1.height, c2.height)
    gw = tw + 12
    canvas = Image.new('RGBA', (gw * 3, th), (255, 255, 255, 255))
    canvas.paste(Image.new('RGBA', (tw, th), DARKBG), (gw, 0))
    canvas.paste(Image.new('RGBA', (tw, th), DARKBG), (gw * 2, 0))
    for i, cc in enumerate([c1, c1, c2]):
        canvas.paste(cc, (i * gw + (tw - cc.width) // 2, (th - cc.height) // 2), cc)
    checks.append(canvas.convert('RGB'))

with open(os.path.join(OUT, '_palette.json'), 'w', encoding='utf-8') as fp:
    json.dump(report, fp, ensure_ascii=False, indent=1)

cw = max(c.width for c in checks)
chh = sum(c.height for c in checks) + 10 * (len(checks) - 1)
sheet = Image.new('RGB', (cw, chh), (235, 232, 226))
y = 0
for c in checks:
    sheet.paste(c, (0, y)); y += c.height + 10
sheet.save(os.path.join(OUT, 'check.png'))
print('\nDONE ->', OUT)
print('!! 必做：读 assets/check.png 目视核对（左白底 / 中深底 / 右反白深底）')
