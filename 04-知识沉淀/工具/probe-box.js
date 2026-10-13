/* ============================================================
   probe-box.js —— 页面盒子探针（排版疑难杂症的终极诊断工具）

   ⚠️ 本文件刻意在注释里把 HTML 标签的尖括号写成全角/转义形式
      （如 script、body），避免内联进 HTML 时提前闭合 script 标签，
      导致整段代码被当文本渲染出来。
      （这是 JS 内联的经典坑，2026-09-17 实测踩到过。）

   用法 A · 外部引用（推荐）
     用 script 标签引用本文件，并加 data-probe 属性：
       script src="probe-box.js" data-probe=".slide,.dv-wrap,.deck"

   用法 B · 内联
     把本文件内容塞进一个 script 标签，附在 body 结束前。
     内联时 document.currentScript 有效，data-probe 也可用。

   全局兜底：
     可在调用前设 window.__PROBE__ = '.slide,.deck' 指定选择器。

   为什么需要它：
     "计算样式全对、渲染却不对"是排版里最难查的一类 bug。
     2026-09-17 的 .slide 高度塌陷（1080px → 144px）就是这样 ——
     top/bottom/inset 计算值全是 0px，只有 getBoundingClientRect 才暴露真相。
     **遇到这类问题，不要再读 CSS 猜，直接量盒子。**

   输出字段：
     rect   getBoundingClientRect() 的**视觉值**（含祖先 transform 的缩放）
     layout **1:1 布局真值** —— 临时摘掉祖先链上所有 transform 后测，再原样恢复
            ⚠️ 带 scale() 的祖先会让 rect 偏大（实测 724 vs 真值 718）。
            要判"尺寸对不对"，**看 layout，别看 rect**。
     css    getComputedStyle 的声明值
     scroll scrollHeight / clientHeight（识别内容溢出）
   ============================================================ */
(function () {
  var sel = (window.__PROBE__)
            || (document.currentScript && document.currentScript.getAttribute('data-probe'))
            || '.deck,.slide';
  var list = sel.split(',').map(function (s) { return s.trim(); }).filter(Boolean);

  var out = [];
  out.push('viewport  ' + window.innerWidth + ' x ' + window.innerHeight);
  out.push('devicePR  ' + (window.devicePixelRatio || 1));
  out.push('');

  // 摘掉祖先链上所有 transform，量一次，再原样恢复 —— 拿 1:1 布局真值。
  // 为什么必须这么做：`.deck` 常带 transform:scale() 做视口适配，
  // getBoundingClientRect 返回的是缩放后的视觉值，还原时引入量化误差
  // （2026-09-18 实测偏大 6px：724 vs 设计值 718）。
  function layoutRect(el) {
    var chain = [];
    var p = el.parentElement;
    while (p && p !== document.documentElement) {
      var t = getComputedStyle(p).transform;
      if (t && t !== 'none') chain.push([p, p.style.transform]);
      p = p.parentElement;
    }
    if (!chain.length) return null;
    chain.forEach(function (it) { it[0].style.transform = 'none'; });
    var r = el.getBoundingClientRect();   // 读值即触发 reflow
    var v = { x: r.x, y: r.y, w: r.width, h: r.height };
    chain.forEach(function (it) { it[0].style.transform = it[1]; });
    return v;
  }

  function dump(el, tag) {
    if (!el) { out.push(tag + '  <<未找到>>'); return; }
    var r = el.getBoundingClientRect();
    var c = getComputedStyle(el);
    out.push(tag);
    out.push('  rect   x=' + r.x.toFixed(1) + ' y=' + r.y.toFixed(1) +
             ' w=' + r.width.toFixed(1) + ' h=' + r.height.toFixed(1));
    var lr = layoutRect(el);
    if (lr) {
      var same = Math.abs(lr.w - r.width) < 0.5 && Math.abs(lr.h - r.height) < 0.5;
      out.push('  layout x=' + lr.x.toFixed(1) + ' y=' + lr.y.toFixed(1) +
               ' w=' + lr.w.toFixed(1) + ' h=' + lr.h.toFixed(1) +
               (same ? '   (与 rect 一致)' : '   <<< 与 rect 不同，判尺寸请以此为准'));
    }
    out.push('  css    h=' + c.height + ' w=' + c.width +
             ' top=' + c.top + ' bottom=' + c.bottom + ' left=' + c.left + ' right=' + c.right);
    out.push('  box    pos=' + c.position + ' disp=' + c.display +
             ' pad=' + c.padding + ' box-sizing=' + c.boxSizing);
    out.push('  overflow=' + c.overflow + ' transform=' + c.transform);
    out.push('  bg=' + c.backgroundColor + '  z=' + c.zIndex);
    var sh = el.scrollHeight, ch = el.clientHeight;
    if (sh !== ch) out.push('  ⚠ scroll  scrollH=' + sh + ' clientH=' + ch +
                            '  (内容溢出 ' + (sh - ch) + 'px)');
  }

  list.forEach(function (s) {
    var nodes = document.querySelectorAll(s);
    if (!nodes.length) { out.push(s + '  <<未找到>>'); out.push(''); return; }
    // 只探前 3 个，避免输出过载
    for (var i = 0; i < Math.min(nodes.length, 3); i++) {
      dump(nodes[i], s + (nodes.length > 1 ? ' [' + (i + 1) + ']' : ''));
    }
    out.push('');
  });

  // 关键诊断：找出「高宽比异常」的元素 —— 满幅层高度明显小于其父层时报警
  var deck = document.querySelector('.deck');
  if (deck) {
    var dh = deck.getBoundingClientRect().height;
    out.push('--- 满幅层体检（父 .deck 高 ' + dh.toFixed(1) + 'px） ---');
    var suspects = deck.querySelectorAll('.slide, .bleed, .dv-wrap, [class*="full"], [class*="cover"]');
    var bad = 0;
    suspects.forEach(function (el) {
      var h = el.getBoundingClientRect().height;
      if (h > 0 && h < dh * 0.5) {
        bad++;
        out.push('  ⚠ ' + (el.className || el.tagName) + '  h=' + h.toFixed(1) +
                 '  (' + (h / dh * 100).toFixed(0) + '% of deck)  ← 疑似塌陷');
      }
    });
    if (!bad) out.push('  ✅ 未发现塌陷元素');
    out.push('');
    out.push('提示 1：带 transform 的祖先会使子元素 bottom:0 拉伸失效，');
    out.push('        修法 = 给满幅层写死 height:100%。');
    out.push('提示 2：判「尺寸对不对」请读 layout 行（摘掉祖先 transform 的 1:1 真值），');
    out.push('        不要用 rect —— 它含祖先 scale() 的缩放，实测会偏大 6px。');
  }

  var box = document.createElement('div');
  // 固定左上角、限宽限高、内部滚动 —— 内容长也不会溢出屏幕看不到
  box.style.cssText = 'position:fixed;left:0;top:0;z-index:2147483647;' +
    'background:#ffff00;color:#000;font:12px/1.5 ui-monospace,Consolas,monospace;' +
    'padding:10px 14px;white-space:pre;overflow:auto;' +
    'max-width:min(760px,86vw);max-height:96vh;' +
    'border:2px solid #f00;box-shadow:0 4px 20px rgba(0,0,0,.4)';
  box.textContent = out.join('\n');
  document.body.appendChild(box);

  // 关键结论同时写进 document.title，便于无 GUI 场景直接取文本
  var warn = out.filter(function (l) { return l.indexOf('⚠') >= 0; });
  document.title = warn.length ? ('PROBE-WARN: ' + warn[0].trim()) : 'PROBE-OK';
})();
