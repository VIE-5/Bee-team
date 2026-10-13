# -*- coding: utf-8 -*-
"""溢出探针（probe_overflow.py）—— 逐页量「内容实际底部 vs 容器底部」，
抓出被 overflow:hidden 静默裁掉的内容（文本块 / 栅格 / 列表，不只是图片）。

为什么需要它
------------
页数 / 体积分布 / md5 唯一数 / PDF 页数 & MediaBox —— 这些收尾指标
在**内容溢出被裁**的情况下全部正常：溢出部分根本不进入产物，册子"看起来"完整。
`probe_fit.py` 只查图片；文本与栅格的溢出要靠本工具。

典型案例（2026-09-27 碗香第 5 轮）：目录页 `.toc-wrap` 两列自动行高，
10 个章节块实需 1545px、容器只有 705px → 后 6 个章节**从未出现在目录里**，
而渲染张数 72/72、体积分布正常、md5 唯一数 72、PDF 页数正确 —— 全程无告警。

用法
----
    python probe_overflow.py <index.html> [容器选择器=.bd] [chrome.exe]

输出
----
逐页 `P<n> 内容底=xxx 容器底=xxx fill=NN%`，标 `OVERFLOW` / `EMPTY`；
收尾打印唯一结论 `PASS` / `FAIL(n)`（n = 溢出页数）。
"""
import io
import os
import re
import subprocess
import sys

SRC = os.path.abspath(sys.argv[1])
CONTAINER = sys.argv[2] if len(sys.argv) > 2 else '.bd'
CHROME = sys.argv[3] if len(sys.argv) > 3 else r'C:/Program Files/Google/Chrome/Application/chrome.exe'

if not os.path.exists(SRC):
    print('!! 找不到 %s' % SRC)
    sys.exit(1)

BASE = os.path.dirname(SRC)
OUT = os.path.join(BASE, '_probe-overflow.html')

html = io.open(SRC, encoding='utf-8').read()

PROBE = """
<script>
(function(){
  var SEL = '__SEL__';
  function run(){
    var slides = document.querySelectorAll('.slide');
    for (var i=0;i<slides.length;i++){ slides[i].style.display='block'; }
    var out = [], bad = 0;
    for (var i=0;i<slides.length;i++){
      var s = slides[i];
      var box = s.querySelector(SEL) || s;
      var br = box.getBoundingClientRect();
      if (br.height < 10){ out.push('P'+(i+1)+'  (无内容容器)'); continue; }
      var maxb = -1e9, all = box.querySelectorAll('*');
      for (var j=0;j<all.length;j++){
        var el = all[j];
        if (el.offsetHeight < 1 && el.offsetWidth < 1) continue;
        var r = el.getBoundingClientRect();
        if (r.bottom > maxb) maxb = r.bottom;
      }
      if (maxb < -1e8) maxb = br.top;
      var over = maxb - br.bottom;
      var fill = (maxb - br.top) / br.height * 100;
      var flag = '';
      if (over > 1.5){ flag = '  << OVERFLOW'; bad++; }
      else if (fill < 60){ flag = '  (偏空)'; }
      out.push('P'+(i+1)+'  内容底='+maxb.toFixed(1)+'  容器底='+br.bottom.toFixed(1)
               +'  fill='+fill.toFixed(0)+'%'+flag);
    }
    out.push('');
    out.push(bad === 0 ? 'PASS' : ('FAIL(' + bad + ')'));
    var A = '@@' + 'OVF' + '_' + 'START' + '@@';
    var B = '@@' + 'OVF' + '_' + 'END' + '@@';
    var pre = document.createElement('pre');
    pre.textContent = '\\n' + A + '\\n' + out.join('\\n') + '\\n' + B + '\\n';
    document.body.appendChild(pre);
  }
  if (document.readyState === 'complete') run();
  else window.addEventListener('load', run);
})();
</script>
""".replace('__SEL__', CONTAINER)

html2 = html.replace('</body>', PROBE + '</body>') if '</body>' in html else html + PROBE
io.open(OUT, 'w', encoding='utf-8').write(html2)

url = 'file:///' + OUT.replace('\\', '/')
cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
       '--user-data-dir=' + os.path.join(BASE, '_work', 'chrome-probe'),
       '--force-device-scale-factor=1', '--window-size=1360,850',
       '--virtual-time-budget=8000', '--dump-dom', url]
res = subprocess.run(cmd, capture_output=True)
dom = res.stdout.decode('utf-8', 'replace')
m = re.search(r'@@OVF_START@@(.*?)@@OVF_END@@', dom, re.S)
if not m:
    print('!! 探针未回传（检查 Chrome 路径与页面是否可加载）')
    sys.exit(1)

lines = m.group(1).strip().split('\n')
print('文件: %s' % os.path.basename(SRC))
print('容器选择器: %s' % CONTAINER)
print('-' * 52)
for l in lines:
    print(l)
