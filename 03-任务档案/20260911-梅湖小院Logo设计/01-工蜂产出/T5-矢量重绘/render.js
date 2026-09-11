// SVG → PNG 光栅化（透明背景，多尺寸）
const { Resvg } = require('@resvg/resvg-js');
const fs = require('fs');
const path = require('path');

const srcDir = process.argv[2];
const outDir = process.argv[3];
const sizes = [1024, 512, 256, 96];

fs.mkdirSync(outDir, { recursive: true });
const files = fs.readdirSync(srcDir).filter(f => f.endsWith('.svg'));

for (const f of files) {
  const svg = fs.readFileSync(path.join(srcDir, f), 'utf8');
  const base = f.replace(/\.svg$/, '');
  for (const w of sizes) {
    const r = new Resvg(svg, {
      fitTo: { mode: 'width', value: w },
      background: 'rgba(0,0,0,0)',
    });
    fs.writeFileSync(path.join(outDir, `${base}_${w}.png`), r.render().asPng());
  }
  console.log(`${base} -> ${sizes.join('/')} OK`);
}
