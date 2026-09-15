# -*- coding: utf-8 -*-
"""
把一整个 deck 的页面缩略图拼成「联系表」(contact sheet)，一次扫 12 页。
用途：快速把握页序与版面节奏，再挑代表页精读。
"""
import os
import sys
import re
from PIL import Image, ImageDraw, ImageFont

TW = 620          # 缩略图宽
COLS, ROWS = 3, 4
GAP = 14
LABEL = 30        # 页码条高
PAD = 18


def natkey(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]


def get_font(sz):
    for p in [r'C:\Windows\Fonts\msyhbd.ttc', r'C:\Windows\Fonts\msyh.ttc',
              r'C:\Windows\Fonts\arialbd.ttf', r'C:\Windows\Fonts\arial.ttf']:
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            continue
    return ImageFont.load_default()


def main():
    deck_dir = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    name = os.path.basename(deck_dir.rstrip('/\\'))

    imgs = sorted([f for f in os.listdir(deck_dir)
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))], key=natkey)
    if not imgs:
        print('no images in', deck_dir)
        return

    f_page = get_font(17)
    per = COLS * ROWS
    n_sheets = (len(imgs) + per - 1) // per
    made = []

    for si in range(n_sheets):
        chunk = imgs[si * per:(si + 1) * per]
        sample = Image.open(os.path.join(deck_dir, chunk[0]))
        th = int(TW * sample.height / sample.width)
        sample.close()

        W = PAD * 2 + COLS * TW + (COLS - 1) * GAP
        H = PAD * 2 + ROWS * (th + LABEL) + (ROWS - 1) * GAP
        sheet = Image.new('RGB', (W, H), (238, 238, 238))
        d = ImageDraw.Draw(sheet)

        for i, fn in enumerate(chunk):
            r, c = divmod(i, COLS)
            x = PAD + c * (TW + GAP)
            y = PAD + r * (th + LABEL + GAP)
            try:
                im = Image.open(os.path.join(deck_dir, fn)).convert('RGB')
                im = im.resize((TW, th), Image.LANCZOS)
                sheet.paste(im, (x, y))
                im.close()
            except Exception as e:
                d.rectangle([x, y, x + TW, y + th], fill=(200, 60, 60))
                d.text((x + 8, y + 8), 'ERR', font=f_page, fill=(255, 255, 255))
            # 页码条
            d.rectangle([x, y + th, x + TW, y + th + LABEL], fill=(32, 32, 36))
            pg = si * per + i + 1
            d.text((x + 9, y + th + 6), 'P%02d  %s' % (pg, fn), font=f_page, fill=(255, 255, 255))

        out = os.path.join(out_dir, '%s_联系表%02d.png' % (re.sub(r'[\\/:*?"<>|]', '_', name), si + 1))
        sheet.save(out)
        made.append(out)
        sheet.close()
        print('OK', os.path.basename(out))

    print('\n%s: %d 页 -> %d 张联系表' % (name, len(imgs), len(made)))


if __name__ == '__main__':
    main()
