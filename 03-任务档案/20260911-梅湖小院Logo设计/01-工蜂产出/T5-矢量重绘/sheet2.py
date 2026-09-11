import os, sys
from PIL import Image

base = os.path.dirname(os.path.abspath(__file__))
sub = sys.argv[1] if len(sys.argv) > 1 else "fin"
names = sys.argv[2].split(",") if len(sys.argv) > 2 else ["01-mei-seal", "02-fish-moon", "03-seal-fish"]
png_dir = os.path.join(base, sub, "png")

cell, cols = 400, len(names)
rows = 1
sheet = Image.new("RGB", (cols * cell, rows * cell), (236, 236, 231))
for i, n in enumerate(names):
    im = Image.open(os.path.join(png_dir, n + "_512.png")).convert("RGBA")
    im = im.resize((cell - 64, cell - 64), Image.LANCZOS)
    tile = Image.new("RGBA", (cell, cell), (236, 236, 231, 255))
    tile.paste(im, ((cell - im.width) // 2, (cell - im.height) // 2), im)
    sheet.paste(tile.convert("RGB"), (i * cell, 0))
out = os.path.join(base, "_contact-sheet.png")
sheet.save(out)
print("saved:", out, sheet.size)
