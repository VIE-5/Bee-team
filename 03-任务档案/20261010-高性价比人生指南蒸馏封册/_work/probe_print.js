// CDP 探针：在 print 媒体下量真实布局，定位目录页的溢出来源
const { spawn } = require('child_process');
const path = require('path');
const { pathToFileURL } = require('url');

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9333;
const DECK = process.argv[2] || path.join(__dirname, '..', '01-工蜂产出', 'T3-版式', 'index.html');
const PROFILE = path.join(require('os').homedir(), '_chrome_cdp_profile');

const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const chrome = spawn(CHROME, [
    '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
    '--force-device-scale-factor=1',
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${PROFILE}`,
    'about:blank',
  ], { stdio: 'ignore' });

  let ver = null;
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      ver = await r.json();
      break;
    } catch (e) { await sleep(250); }
  }
  if (!ver) { console.error('chrome 起不来'); chrome.kill(); process.exit(1); }

  const url = pathToFileURL(DECK).href + '?v=' + Date.now();
  const tr = await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(url)}`, { method: 'PUT' });
  const target = await tr.json();
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  let id = 0;
  const pending = new Map();
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  });
  await new Promise(r => ws.addEventListener('open', r));
  const send = (method, params = {}) => new Promise(res => {
    const i = ++id; pending.set(i, res);
    ws.send(JSON.stringify({ id: i, method, params }));
  });

  await send('Page.enable');
  await send('Emulation.setEmulatedMedia', { media: 'print' });
  await send('Page.navigate', { url });
  await sleep(2500);

  const expr = `(() => {
    const out = { body: document.body.scrollHeight, docEl: document.documentElement.scrollHeight, slides: [], tocDetail: null };
    const ss = [...document.querySelectorAll('.slide')];
    out.count = ss.length;
    ss.slice(0, 6).forEach((s, i) => {
      const r = s.getBoundingClientRect();
      const cs = getComputedStyle(s);
      // 子树最大 bottom（相对 slide 顶）
      let maxB = 0, who = '';
      s.querySelectorAll('*').forEach(e => {
        const er = e.getBoundingClientRect();
        const rel = er.bottom - r.top;
        if (rel > maxB) { maxB = rel; who = e.className || e.tagName; }
      });
      out.slides.push({ i, top: +(r.top + window.scrollY).toFixed(2), h: +r.height.toFixed(2),
        bw: +r.width.toFixed(2), maxBottomRel: +maxB.toFixed(2), worst: String(who).slice(0, 60),
        display: cs.display, position: cs.position, overflow: cs.overflow,
        breakAfter: cs.breakAfter || cs.pageBreakAfter });
    });
    const toc = document.querySelector('.toc');
    if (toc) {
      const r = toc.getBoundingClientRect();
      const sr = toc.closest('.slide').getBoundingClientRect();
      const cs = getComputedStyle(toc);
      const kids = [...toc.children].map(k => {
        const kr = k.getBoundingClientRect();
        return { cls: k.className, h: +kr.height.toFixed(2), topRel: +(kr.top - r.top).toFixed(2), botRel: +(kr.bottom - r.top).toFixed(2) };
      });
      out.tocDetail = { slideH: +sr.height.toFixed(2), topRelSlide: +(r.top - sr.top).toFixed(2),
        h: +r.height.toFixed(2), scrollH: toc.scrollHeight, clientH: toc.clientHeight,
        position: cs.position, kids };
    }
    return JSON.stringify(out);
  })()`;
  const res = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(JSON.parse(res.result.result.value), null, 2));

  ws.close(); chrome.kill();
})();
