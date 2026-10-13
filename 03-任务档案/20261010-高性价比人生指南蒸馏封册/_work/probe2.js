// CDP 探针 2：节点级定位那 22px 匿名盒；并做「body font-size:0」对照
const { spawn } = require('child_process');
const path = require('path');
const { pathToFileURL } = require('url');
const os = require('os');

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9334;
const DECK = path.join(__dirname, '..', '01-工蜂产出', 'T3-版式', 'index.html');
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const chrome = spawn(CHROME, ['--headless=new', '--disable-gpu', '--no-sandbox',
    '--hide-scrollbars', '--force-device-scale-factor=1',
    `--remote-debugging-port=${PORT}`, `--user-data-dir=${path.join(os.homedir(), '_chrome_cdp_profile')}`,
    'about:blank'], { stdio: 'ignore' });
  let ok = false;
  for (let i = 0; i < 60; i++) { try { await fetch(`http://127.0.0.1:${PORT}/json/version`); ok = true; break; } catch { await sleep(250); } }
  if (!ok) { chrome.kill(); process.exit(1); }
  const url = pathToFileURL(DECK).href + '?v=' + Date.now();
  const t = await (await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(url)}`, { method: 'PUT' })).json();
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map();
  ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } });
  await new Promise(r => ws.addEventListener('open', r));
  const send = (method, params = {}) => new Promise(res => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
  await send('Page.enable');
  await send('Emulation.setEmulatedMedia', { media: 'print' });
  await send('Page.navigate', { url });
  await sleep(2500);

  const js = `(() => {
    const report = {};
    const Y = () => window.scrollY;
    const listKids = () => {
      const arr = [];
      document.body.childNodes.forEach((n, idx) => {
        if (n.nodeType === 1) {
          const r = n.getBoundingClientRect();
          arr.push({ idx, type:'E', name:n.tagName + '.' + (n.className||''), top:+(r.top+Y()).toFixed(2), h:+r.height.toFixed(2) });
        } else if (n.nodeType === 3) {
          const rng = document.createRange(); rng.selectNodeContents(n);
          const rects = [...rng.getClientRects()].map(r => ({ top:+(r.top+Y()).toFixed(2), h:+r.height.toFixed(2), w:+r.width.toFixed(2) }));
          arr.push({ idx, type:'T', name: JSON.stringify(n.data), rects });
        } else arr.push({ idx, type:'?', name:n.nodeName });
      });
      return arr;
    };
    report.bodyFont = getComputedStyle(document.body).fontSize + ' / lh=' + getComputedStyle(document.body).lineHeight;
    report.before = listKids().filter(k => k.idx < 8 || k.idx > document.body.childNodes.length - 4);
    report.gapCheck = (() => {
      const ss = [...document.querySelectorAll('.slide')].slice(0, 4).map(s => +(s.getBoundingClientRect().top + Y()).toFixed(2));
      return ss;
    })();
    // 对照实验：把 body 字号归零
    document.body.style.fontSize = '0px';
    void document.body.offsetHeight;
    report.after_font0 = [...document.querySelectorAll('.slide')].slice(0, 4).map(s => +(s.getBoundingClientRect().top + Y()).toFixed(2));
    document.body.style.fontSize = '';
    void document.body.offsetHeight;
    report.after_restore = [...document.querySelectorAll('.slide')].slice(0, 4).map(s => +(s.getBoundingClientRect().top + Y()).toFixed(2));
    // 对照实验 2：把两个 section 之间的空白节点删掉
    for (let i = document.body.childNodes.length - 1; i >= 0; i--) {
      const n = document.body.childNodes[i];
      if (n.nodeType === 3 && !n.data.trim()) n.remove();
    }
    void document.body.offsetHeight;
    report.after_del_ws = [...document.querySelectorAll('.slide')].slice(0, 4).map(s => +(s.getBoundingClientRect().top + Y()).toFixed(2));
    return JSON.stringify(report);
  })()`;
  const r = await send('Runtime.evaluate', { expression: js, returnByValue: true });
  console.log(JSON.stringify(JSON.parse(r.result.result.value), null, 2));
  ws.close(); chrome.kill();
})();
