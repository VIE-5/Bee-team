/* 针对性探针：全页溢出体检 + 关键元素真实落位
   结果写进 #PROBEOUT，用 chrome --dump-dom 取回。 */
(function () {
  var out = [];
  var slides = document.querySelectorAll('.slide');
  var deck = document.querySelector('.deck');
  out.push('slides=' + slides.length);
  var dr = deck.getBoundingClientRect();
  out.push('deck=' + dr.width.toFixed(1) + 'x' + dr.height.toFixed(1));

  var bad = 0;
  for (var i = 0; i < slides.length; i++) {
    var s = slides[i];
    var sr = s.getBoundingClientRect();
    var bd = s.querySelector('.bd');
    if (bd) {
      var o = bd.scrollHeight - bd.clientHeight;
      if (o > 1) { out.push('P' + (i + 1) + ' .bd OVERFLOW ' + o + 'px (scrollH=' + bd.scrollHeight + ' clientH=' + bd.clientHeight + ')'); bad++; }
    }
    var all = s.querySelectorAll('*');
    for (var j = 0; j < all.length; j++) {
      var el = all[j];
      if (el.id === 'PROBEOUT') continue;
      var r = el.getBoundingClientRect();
      if (r.width < 1 && r.height < 1) continue;
      var over = [];
      if (r.bottom > sr.bottom + 0.5) over.push('B+' + (r.bottom - sr.bottom).toFixed(0));
      if (r.top < sr.top - 0.5) over.push('T-' + (sr.top - r.top).toFixed(0));
      if (r.right > sr.right + 0.5) over.push('R+' + (r.right - sr.right).toFixed(0));
      if (r.left < sr.left - 0.5) over.push('L-' + (sr.left - r.left).toFixed(0));
      if (over.length) {
        out.push('P' + (i + 1) + ' OUT ' + (el.className || el.tagName) + ' [' + over.join(' ') + ']');
        bad++;
      }
    }
  }
  out.push('problems=' + bad);

  // P05 图像落位
  var p5 = slides[4];
  if (p5) {
    var st = p5.querySelectorAll('.lc-stage');
    var im = p5.querySelectorAll('.lc-stage img');
    for (var k = 0; k < im.length; k++) {
      var ir = im[k].getBoundingClientRect();
      var sr2 = st[k].getBoundingClientRect();
      out.push('P5 cell' + (k + 1) + ' stage=' + sr2.width.toFixed(1) + 'x' + sr2.height.toFixed(1) +
               ' img=' + ir.width.toFixed(1) + 'x' + ir.height.toFixed(1) +
               ' ar=' + (ir.width / ir.height).toFixed(4) +
               ' nat=' + im[k].naturalWidth + 'x' + im[k].naturalHeight +
               ' overflowH=' + (ir.bottom - sr2.bottom).toFixed(1));
    }
  }

  // P06 / P07 图台
  var dl = document.querySelectorAll('.draft-stage');
  for (var m = 0; m < dl.length; m++) {
    var drr = dl[m].getBoundingClientRect();
    var svg = dl[m].querySelector('svg');
    var g = svg ? svg.getBoundingClientRect() : null;
    out.push('draft' + (m + 1) + ' stage=' + drr.width.toFixed(1) + 'x' + drr.height.toFixed(1) +
             (g ? ' svg=' + g.width.toFixed(1) + 'x' + g.height.toFixed(1) : ' svg=none'));
  }

  // 字体是否真的加载（判断 Noto Serif SC 有没有到位）
  out.push('fontsReady=' + (document.fonts ? document.fonts.status : 'n/a'));

  var box = document.createElement('div');
  box.id = 'PROBEOUT';
  box.style.cssText = 'position:fixed;left:0;top:0;z-index:99999;background:#ff0;color:#000;' +
    'font:11px/1.4 monospace;white-space:pre;max-height:100vh;overflow:auto';
  box.textContent = '\n' + out.join('\n') + '\n';
  document.body.appendChild(box);
})();
