# -*- coding: utf-8 -*-
r"""图版贴合探针（probe_fit.py）—— 给一份 deck 的 index.html，逐张图量「渲染尺寸 vs 容器尺寸」，
判定是否存在「图片按原尺寸渲染、被 overflow:hidden 裁掉」这一类静默缺陷。

为什么需要它
------------
「固定画布下尺寸一律硬编码 px」（2026-09-18 立为铁律）在同一份册子上**复发过一次**：
把本来正确的 `max-width:1054px; max-height:676px` 换成 `max-width:100%; max-height:100%` 后，
容器高度由 flex 拉伸而来（height 属性仍是 auto）→ 百分比上限被 Chrome 解析为 none →
图片退回原尺寸 → 被 `.frame{overflow:hidden}` 裁掉（板图左右各裁 260px、竖版图上下各裁 495px，
4 张主题海报头尾全丢）。而当时的收尾验收只查了「张数 + 体积分布 + 退出码 0」，
**这三项全过** —— 缺口就在这里，本工具是该铁律的机检出口。

用法
----
    python probe_fit.py <index.html> [slide选择器=\.slide] [chrome.exe]

    # 例
    python probe_fit.py D:/.../01-工蜂产出/index.html

判据（全部由浏览器实测，不读 CSS）
--------------------------------
  1. CROP    —— img 渲染宽/高 > 容器 padding box 宽/高  → 图片被裁
  2. DISTORT —— img 渲染宽高比 != naturalWidth/naturalHeight（容差 0.6%）→ 图片变形
  3. 器高塌陷 —— 容器高 == 0 而图高 > 0 → 容器没撑起来（多为父级丢高度）

收尾打印唯一结论：PASS / FAIL(n)；FAIL 时逐条列出页码与数值。
"""
import io
import os
import re
import subprocess
import sys
from pathlib import Path

CHROME_DEFAULT = r'C:/Program Files/Google/Chrome/Application/chrome.exe'

JS = """
<script>
(function(){
  function run(){
    var sel = "%(SEL)s";
    var all = document.querySelectorAll(sel);
    for (var i=0;i<all.length;i++){ all[i].style.display='block'; }
    var out = [];
    var imgs = document.querySelectorAll('img');
    for (var j=0;j<imgs.length;j++){
      var im = imgs[j];
      var cs = getComputedStyle(im);
      if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      var r = im.getBoundingClientRect();
      if (r.width < 1 || r.height < 1) continue;
      var p = im.parentElement;
      var pcs = getComputedStyle(p);
      var pw = p.clientWidth - parseFloat(pcs.paddingLeft || 0) - parseFloat(pcs.paddingRight || 0);
      var ph = p.clientHeight - parseFloat(pcs.paddingTop || 0) - parseFloat(pcs.paddingBottom || 0);
      // 找到所属页序号
      var pg = 0, n = im;
      while (n && n !== document.body){ if (n.matches && n.matches(sel)) { pg = 1 + [].indexOf.call(document.querySelectorAll(sel), n); break; } n = n.parentElement; }
      out.push([pg, im.naturalWidth, im.naturalHeight, Math.round(r.width*100)/100, Math.round(r.height*100)/100,
                Math.round(pw*100)/100, Math.round(ph*100)/100, pcs.overflow, im.getAttribute('src')||''].join('\\t'));
    }
    var A = '@@' + 'FIT' + '_' + 'START' + '@@';
    var B = '@@' + 'FIT' + '_' + 'END' + '@@';
    var pre = document.createElement('pre');
    pre.textContent = '\\n' + A + '\\n' + out.join('\\n') + '\\n' + B + '\\n';
    document.body.appendChild(pre);
  }
  if (document.readyState === 'complete') run();
  else window.addEventListener('load', run);
})();
</script>
"""


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    src = Path(sys.argv[1]).resolve()
    sel = sys.argv[2] if len(sys.argv) > 2 else '.slide'
    chrome = sys.argv[3] if len(sys.argv) > 3 else CHROME_DEFAULT
    if not src.exists():
        print('[ERR] 找不到', src)
        return 2
    if not Path(chrome).exists():
        print('[ERR] 找不到 Chrome：', chrome)
        return 2

    html = io.open(src, encoding='utf-8').read()
    probe = JS % {'SEL': sel}
    dst = src.with_name('_probe-fit.html')
    io.open(dst, 'w', encoding='utf-8').write(
        html.replace('</body>', probe + '</body>') if '</body>' in html else html + probe)

    cmd = [chrome, '--headless=new', '--disable-gpu', '--no-sandbox',
           '--user-data-dir=' + str(src.parent / '_work' / 'chrome-probe'),
           '--force-device-scale-factor=1', '--window-size=1360,850',
           '--virtual-time-budget=10000', '--dump-dom', dst.as_uri()]
    dom = subprocess.run(cmd, capture_output=True).stdout.decode('utf-8', 'replace')
    m = re.search(r'@@FIT_START@@(.*?)@@FIT_END@@', dom, re.S)
    if not m:
        print('[ERR] 探针未回传（检查 index.html 是否有 </body>、选择器是否正确）')
        return 2

    rows = [l for l in m.group(1).strip().split('\n') if l.strip()]
    if not rows:
        print('[ERR] 没有量到任何图片')
        return 2

    bad = []
    n_crop = n_dist = n_coll = 0
    for line in rows:
        f = line.split('\t')
        pg = int(f[0]); nw, nh = int(f[1]), int(f[2])
        rw, rh = float(f[3]), float(f[4])
        pw, ph = float(f[5]), float(f[6])
        ov, s = f[7], f[8]
        if nw > 0 and nh > 0:
            ar_n = nw / nh
            ar_r = rw / rh
            if abs(ar_r - ar_n) / ar_n > 0.006:
                n_dist += 1
                bad.append('DISTORT  P%-3d  nat %dx%d  渲染 %.1fx%.1f  比例 %.4f vs %.4f  %s'
                           % (pg, nw, nh, rw, rh, ar_r, ar_n, s))
        if pw > 0 and ph > 0 and (rw > pw + 1.0 or rh > ph + 1.0):
            n_crop += 1
            bad.append('CROP     P%-3d  图 %.1fx%.1f > 容器 %.1fx%.1f（overflow:%s）  %s'
                       % (pg, rw, rh, pw, ph, ov, s))
        if ph < 1 and rh > 1:
            n_coll += 1
            bad.append('COLLAPSE P%-3d  容器高 0 而图高 %.1f  %s' % (pg, rh, s))

    print('图片总数 =', len(rows))
    print('CROP = %d   DISTORT = %d   容器高塌陷 = %d' % (n_crop, n_dist, n_coll))
    if bad:
        print('--- 问题明细 ---')
        for b in bad[:80]:
            print(' ', b)
        if len(bad) > 80:
            print('  ... 另有 %d 条' % (len(bad) - 80))
        print('结论：FAIL(%d)' % len(bad))
        return 1
    print('结论：PASS —— 全部图片贴合容器，无裁切 / 无变形')

    try:
        dst.unlink()
    except OSError:
        pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
