import os
from PIL import Image

base = os.path.dirname(os.path.abspath(__file__))
png_dir = os.path.join(base, "png")
names = ["A-final", "B-final", "C1-final", "C3-seal-gate"]
cell, cols = 400, 2
rows = (len(names) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell, rows * cell), (236, 236, 231))

for i, n in enumerate(names):
    im = Image.open(os.path.join(png_dir, n + "_512.png")).convert("RGBA")
    im = im.resize((cell - 56, cell - 56), Image.LANCZOS)
    tile = Image.new("RGBA", (cell, cell), (236, 236, 231, 255))
    tile.paste(im, ((cell - im.width) // 2, (cell - im.height) // 2), im)
    r, c = divmod(i, cols)
    sheet.paste(tile.convert("RGB"), (c * cell, r * cell))

out = os.path.join(base, "_contact-sheet.png")
sheet.save(out)
print("saved:", out, sheet.size)
