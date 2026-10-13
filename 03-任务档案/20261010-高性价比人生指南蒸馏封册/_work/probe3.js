const { spawn } = require('child_process');
const path = require('path'), os = require('os');
const { pathToFileURL } = require('url');
const CHROME = 'C://Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9335;
const DECK = path.join(__dirname, '..', '01-工蜂产出', 'T3-版式', 'index.html');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const chrome = spawn(CHROME, ['--headless=new','--disable-gpu','--no-sandbox','--hide-scrollbars',
    '--force-device-scale-factor=1',`--remote-debugging-port=${PORT}`,
    `--user-data-dir=${path.join(os.homedir(),'_chrome_cdp_profile')}`,'about:blank'],{stdio:'ignore'});
  let ok=false; for(let i=0;i<60;i++){try{await fetch(`http://127.0.0.1:${PORT}/json/version`);ok=true;break;}catch{await sleep(250);}}
  if(!ok){chrome.kill();process.exit(1);}
  const url = pathToFileURL(DECK).href+'?v='+Date.now();
  const t = await (await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(url)}`,{method:'PUT'})).json();
  const ws = new WebSocket(t.webSocketDebuggerUrl); let id=0; const pend=new Map();
  ws.addEventListener('message',e=>{const m=JSON.parse(e.data); if(m.id&&pend.has(m.id)){pend.get(m.id)(m);pend.delete(m.id);}});
  await new Promise(r=>ws.addEventListener('open',r));
  const send=(method,params={})=>new Promise(res=>{const i=++id;pend.set(i,res);ws.send(JSON.stringify({id:i,method,params}));});
  await send('Page.enable'); await send('Emulation.setEmulatedMedia',{media:'print'});
  await send('Page.navigate',{url}); await sleep(2200);
  const js=`(()=>{const out=[];const ss=[...document.querySelectorAll('.slide')].slice(0,4);
   ss.forEach((s,i)=>{const cs=getComputedStyle(s);const r=s.getBoundingClientRect();
     out.push({i, cls:s.className, top:+(r.top+window.scrollY).toFixed(2),
       marginTop:cs.marginTop, marginBottom:cs.marginBottom, padding:cs.padding,
       borderBottom:cs.borderBottomWidth, display:cs.display, boxSizing:cs.boxSizing, height:cs.height});});
   const hd=document.querySelector('.slide.pg-toc .hd').getBoundingClientRect();
   const sec=document.querySelector('.slide.pg-toc').getBoundingClientRect();
   out.push({probe:'toc .hd 相对 section 顶部偏移', hdTop:+(hd.top-sec.top).toFixed(2)});
   return JSON.stringify(out);})()`;
  const r = await send('Runtime.evaluate',{expression:js,returnByValue:true});
  console.log(JSON.stringify(JSON.parse(r.result.result.value),null,2));
  ws.close(); chrome.kill();
})();
