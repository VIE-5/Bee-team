const { spawn } = require('child_process');
const path = require('path'), os = require('os');
const { pathToFileURL } = require('url');
const CHROME = 'C://Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9336;
const DECK = path.join(__dirname, '..', '01-工蜂产出', 'T3-版式', 'index.html');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const chrome = spawn(CHROME, ['--headless=new','--disable-gpu','--no-sandbox','--hide-scrollbars',
    '--force-device-scale-factor=1','--window-size=794,1123',
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${path.join(os.homedir(),'_chrome_cdp_profile')}`,'about:blank'],{stdio:'ignore'});
  let ok=false; for(let i=0;i<60;i++){try{await fetch(`http://127.0.0.1:${PORT}/json/version`);ok=true;break;}catch{await sleep(250);}}
  if(!ok){chrome.kill();process.exit(1);}
  const url = pathToFileURL(DECK).href+'#/5';
  const t = await (await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(url)}`,{method:'PUT'})).json();
  const ws = new WebSocket(t.webSocketDebuggerUrl); let id=0; const pend=new Map();
  ws.addEventListener('message',e=>{const m=JSON.parse(e.data); if(m.id&&pend.has(m.id)){pend.get(m.id)(m);pend.delete(m.id);}});
  await new Promise(r=>ws.addEventListener('open',r));
  const send=(method,params={})=>new Promise(res=>{const i=++id;pend.set(i,res);ws.send(JSON.stringify({id:i,method,params}));});
  await send('Page.enable'); await send('Page.navigate',{url}); await sleep(2000);
  const js=`(()=>{
    const out={};
    const ss=[...document.querySelectorAll('.slide')];
    out.media='screen';
    out.activePage = ss.findIndex(s=>s.classList.contains('on'))+1;
    const toc=ss[2];
    // A: 现状（pg-toc + 内联 display 由路由写）
    out.A_current = {cls: toc.className, inlineDisplay: toc.style.display, computed: getComputedStyle(toc).display};
    // B: 还原成故障时的写法 —— 去掉内联，类名换回 toc-p
    toc.style.display='';            // 摘掉内联覆盖
    toc.className='slide toc-p';     // 还原撞车类名
    out.B_collide = {cls: toc.className, computed: getComputedStyle(toc).display};
    // C: 对照 —— 类名换回 pg-toc，仍无内联
    toc.className='slide pg-toc';
    out.C_renamed = {cls: toc.className, computed: getComputedStyle(toc).display};
    // D: 无内联时，非活动页的 .slide 计算值
    const other=ss[5]; other.style.display='';
    out.D_others = {cls: other.className, computed: getComputedStyle(other).display};
    return JSON.stringify(out);})()`;
  const r = await send('Runtime.evaluate',{expression:js,returnByValue:true});
  console.log(JSON.stringify(JSON.parse(r.result.result.value),null,2));
  ws.close(); chrome.kill();
})();
