# -*- coding: utf-8 -*-
"""v3 交付终检：PDF 页数/尺寸/字体/图像 + PNG 唯一性 + 素材尺寸。"""
import os, re, hashlib, sys
from PIL import Image

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '01-工蜂产出')
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print('BASE =', BASE)
print('exists:', os.path.isdir(BASE))
print('=' * 58)

# ---- PDF ----
pdfs = [f for f in os.listdir(BASE) if f.lower().endswith('.pdf')]
print('[PDF]')
for f in sorted(pdfs):
    p = os.path.join(BASE, f)
    b = open(p, 'rb').read()
    pages = len(re.findall(rb'/Type\s*/Page[^s]', b))
    mb = set(re.findall(rb'/MediaBox\s*\[([^\]]+)\]', b))
    fonts = len(re.findall(rb'/Type\s*/Font', b))
    imgs = len(re.findall(rb'/Subtype\s*/Image', b))
    print('  %-34s %7.1f MB  pages=%-3d fonts=%-4d imgs=%-3d' % (f, len(b) / 1048576, pages, fonts, imgs))
    for m in mb:
        vals = [float(x) for x in m.split()]
        w, h = vals[2] - vals[0], vals[3] - vals[1]
        print('      MediaBox %s -> %.1f x %.1f pt  (ratio %.4f, expect %.4f)'
              % (m.decode(), w, h, w / h, 16 / 10))

# ---- PNG ----
print('[PNG]')
png_dir = os.path.join(BASE, 'png')
names = sorted(f for f in os.listdir(png_dir) if f.endswith('.png') and f.startswith('slide-'))
hashes, sizes = {}, set()
for n in names:
    with open(os.path.join(png_dir, n), 'rb') as fh:
        hashes.setdefault(hashlib.md5(fh.read()).hexdigest(), []).append(n)
    with Image.open(os.path.join(png_dir, n)) as im:
        sizes.add(im.size)
print('  slide count      :', len(names))
print('  unique md5       :', len(hashes))
dups = {k: v for k, v in hashes.items() if len(v) > 1}
print('  duplicated groups:', len(dups))
for k, v in dups.items():
    print('     !!', v)
print('  distinct sizes   :', sizes)
sheet = os.path.join(png_dir, '_contact-sheet.png')
if os.path.exists(sheet):
    with Image.open(sheet) as im:
        print('  contact sheet    : %dx%d  %.1f MB'
              % (im.size[0], im.size[1], os.path.getsize(sheet) / 1048576))

# ---- assets ----
print('[ASSETS]')
ad = os.path.join(BASE, 'assets')
wp = sorted(f for f in os.listdir(ad) if f.endswith('.webp'))
print('  webp count:', len(wp))
tot = 0
for f in wp:
    p = os.path.join(ad, f)
    tot += os.path.getsize(p)
    with Image.open(p) as im:
        w, h = im.size
    print('    %-24s %4dx%-5d %7.0f KB' % (f, w, h, os.path.getsize(p) / 1024))
print('  assets total: %.1f MB' % (tot / 1048576))

# ---- html 硬编码字距残留 ----
print('[HTML]')
hp = os.path.join(BASE, 'index.html')
html = open(hp, encoding='utf-8').read()
resid = re.findall(r'letter-spacing\s*:\s*([0-9.]+em)', html)
print('  inline letter-spacing(em) residuals:', len(resid), sorted(set(resid)))
print('  var(--ls-*) usages:', len(re.findall(r'var\(--ls-', html)))
