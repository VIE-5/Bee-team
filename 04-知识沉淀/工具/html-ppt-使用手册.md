# html-ppt-studio 使用手册（Windows）v2

> 引入日期：2026-09-15 ｜ 来源：https://github.com/lewislulu/html-ppt-skill ｜ 许可：MIT
> 安装位置：`C:\Users\27612\.workbuddy\skills\html-ppt`
> v2 更新（2026-09-17）：补「自建主题六大铁律」+ 换用 `render-deck.py`，来自土蚝小院 29 页实战

## 一句话定位
**图片素材 → 润色 / 排版 / 封装成提案 deck** 的产线。适合「主人出图，skill 排版」的工作流。

## 能力清单（已实测）

| 能力 | 实现方式 | 实测结论 |
|---|---|---|
| 接外部图片 | `<figure class="img-frame"><img src="…"></figure>` | ✅ 可用 |
| 图片不裁切 | 加 `.contain` class | ✅ 三张不同比例图统一切齐 |
| 图片裁切填满 | 默认（不加 .contain） | ✅ |
| 比例控制 | `--img-ratio` CSS 变量 | ✅ |
| 位置控制 | `--img-pos`（如 `top`） | ✅ |
| 一键 Logo | `<body data-logo="logo.svg" data-logo-position="bottom-right">` | ✅ 右下角水印生效 |
| 封面跳过 Logo | `<section data-no-logo>` | ✅ |
| 品牌色换肤 | 自建一个主题 CSS 文件，覆盖 `:root` 变量 | ✅ |
| 导出 PNG | Chrome headless `--screenshot` | ✅ |
| 导出 PDF | Chrome headless `--print-to-pdf` | ✅ 5 页 = 5 张 slide |

## 资源盘点
- **36 个主题**：`assets/themes/*.css`，纯 CSS 变量，换一行 `<link>` 即整套换肤
- **36 个单页版式**：`templates/single-page/*.html`（含 5 个图片专用版式）
- **15 套整套模板**：`templates/full-decks/`
- **47 个动效**：27 CSS + 20 Canvas FX

### 图片专用版式（选型指引）
| 你有几张图 | 版式文件 | 特性 |
|---|---|---|
| 1 张（不裁切） | `image-single.html` | letterbox 完整显示 |
| 1 张（撑满整页） | `image-full-bleed.html` | 铺满 + 文字蒙版 |
| 1 张 + 论述 | `image-text-split.html` | 50/50 分栏，`flip` 换边 |
| 3–6 张 | `image-gallery.html` | 统一网格 + 每张说明 |
| 前后对比 | `image-compare.html` | 左右等大 |

## ⚠️ Windows 上的四个坑（原版未覆盖）

> **前置铁律（比下面四条都重要）**：在 Git Bash 里调用**任何外部 Windows 程序**（Chrome / LibreOffice / Node…），
> 传路径**必须用 Windows 风格**（`C:/...`）。Git Bash 只对**纯 ASCII 路径**做 Unix→Windows 转换，
> 蜂巢路径含 `——`（em dash）和中文 → **转换被跳过** → 外部程序收到 `/d/WORK——Vie/...` 这种非法路径，
> **静默零产出（退出码还是 0）**，甚至进程僵死。详见 `04-知识沉淀/踩坑库.md`（2026-09-15 条）。

### 坑 1：`scripts/render.sh` 是 macOS 专用
Chrome 路径写死 `/Applications/Google Chrome.app/...`，Windows 直接报 `Chrome not found`。
**解法**：用 `04-知识沉淀/工具/render-deck.py`（首选）或 `render-win.bat`（应急备用）。

### 坑 2：Chrome headless 必须带 `--user-data-dir`
不带独立 profile 会**静默失败**（退出码 0 但零文件写出）。
**解法**：`--user-data-dir=<临时目录>`，且用完 `rmdir` 清理（否则一次测试就占 40M）。

### 坑 3：跨盘符时资源路径算歪
`new-deck.sh` 的 `relpath()` 在 D 盘 deck + C 盘 skill 时，算出 `../../../../../../../../c/Users/...` 这种畸形路径。
**解法**：deck 建在 skill 目录内（如 `examples/`），或在同盘符下工作。

### 附加坑：README 承诺的部分文件不存在
README 提到 `scripts/export-pdf.sh`，**仓库里实际没有**。PDF 得自己用 Chrome `--print-to-pdf` 出。

### 坑 4：批量渲染/导出后**必须核对产物**，别信退出码
Chrome headless 与 LibreOffice headless 都有「**退出码 0 但零文件**」的失败模式（见坑 2、以及踩坑库
2026-09-15 的 LibreOffice 案例）。渲染/导出命令跑完，**收尾一定 `ls` 数数量、看体积**——
只看「任务完成」会把废品当成品往下传。

### 坑 5：Chrome 缓存 CSS → **改了等于没改**（2026-09-18 碗香单）
改完整套 CSS 重渲染，截图跟改之前**一模一样**，而且「退出码 0 + 文件确实生成了」，
你只会以为自己编辑没落盘。根因是 Chrome 复用 `--user-data-dir` 的磁盘缓存。
**解法：URL 加时间戳 `?v=<ms>`**（render-deck.py 的 `cache_bust()` 已内置）。
凡「改了前端资源重渲染没变化」，先怀疑缓存。

### 坑 6：`<figure>` 的 UA 默认 margin 让网格静默掉列（2026-09-18 碗香单）
`<figure>` 浏览器默认带 `margin: 1em 40px`，用它做网格项时每格凭空多占 80px，
四列网格会悄悄掉成三列 → 行数暴增 → 末行溢出画布被裁。
**解法：`figure{margin:0}`**。同理适用于其他带 UA 默认 margin 的元素。

### 坑 7：输出符号别用 `✓ ✗ ⚠`，用 ASCII
Windows 控制台是 GBK，`print("✓")` 会 `UnicodeEncodeError` **直接崩掉脚本**
（2026-09-18 实测：3 页渲染全成功，却崩在收尾那句，把后面的 PDF 导出整个挤掉）。
**别**改成 `sys.stdout.reconfigure(encoding="utf-8")` —— 那样 PowerShell 又按 GBK 解码，
中文全变 `D:\WORK鈥斺€擵ie\...`。**正解：保留系统编码，符号全换 `[OK] [X] [!]`。**

**另注**：诊断时用 PowerShell 的 `> out.txt 2> err.txt` 分流，产物是 **UTF-16LE**（不是 UTF-8），
读的时候要按 `utf-16` 解，否则会被当成二进制。

---

## ⚠️⚠️ 自建主题六大铁律（v2 新增 · 2026-09-17 土蚝小院实战换来的）

> 这一节比上面所有坑都重要。**自己写主题 CSS 时，这六条任犯一条就整页崩。**

### R1 · 满幅层写死 `height:100%`，绝不只靠 `inset:0`（最致命）

`.deck` 上有 `transform: scale(var(--deck-scale))` 适配视口。
**带 transform 的祖先成为包含块**，Chrome 对子元素 `bottom:0`/`inset:0` 的
「拉伸到父高」解析**失效** → 盒高收缩为内容高度。

实测：`.deck` 高 1080px，`.slide` 只有 **144px** → 墨底页只剩顶部一条，10 页近空白。

```css
/* ✅ */
.slide   { height:100%; }
.dv-wrap { position:absolute; inset:0; height:100%; }
.bleed   { position:absolute; top:-72px; left:-96px; right:-96px; bottom:-72px;
           height:calc(100% + 144px); }
```
探针佐证：`force height:1080px → 1080`、`deck transform:none → 1080`。

### R2 · 内容容器显式 `left/right:var(--mx)`
`.slide` 自带 `padding:72px 96px`（左右 96px ≈ 5%），版心 `--mx` 是 11%。
容器不显式设 left/right 就会继承 padding 起点 → **比页眉更靠左 → 压住竖排边款**。
**页眉 / 正文 / 页脚共用 `--mx` 一条竖线。**

### R3 · 绝不给 `.slide` 写 `padding:0`
会让整页内容消失。满幅用负 margin（`.bleed`），别动 padding。

### R4 · 锁 `@page` 尺寸
```css
@page{ size:1920px 1080px; margin:0; }
```
否则 PDF 落 Letter 白边。导出后核对 MediaBox 比例。

### R5 · 「计算样式全对但渲染不对」→ 上探针，别读 CSS
最隐蔽的一类 bug。用 `04-知识沉淀/工具/probe-box.js` 量 `getBoundingClientRect`，
一次定位。死读 CSS / 二分注释会烧掉数小时。

### R6 · 小体积 PNG ≠ 空白页
墨底满幅页纯色压缩率极高，**20–40KB 属正常**（修好后的分隔页也只 33KB）。
判空白要看内容，或拼联系表通读。

### 附：主题 CSS 必须覆盖 swiss-grid 的背景网格
`swiss-grid.css` 有 `.slide{background-image:linear-gradient(...)}`。
自建主题写 `.slide{background:var(--bg)}`（**简写**）会重置 `background-image`。
**想要网格就别覆盖图片层，不想要就用简写覆盖掉——心里要有数。**

## 标准工作流

```bash
# 1. 脚手架（在 skill 目录内执行，避开跨盘坑）
cd ~/.workbuddy/skills/html-ppt
bash scripts/new-deck.sh <deck名> -t deck

# 2. 放图片
mkdir -p examples/<deck名>/images
# 命名建议 {页号}-{语义}.ext，如 01-logo.png / 03-board.png

# 3. 写品牌主题（复制 theme-brand.css 改色值）
#    色值从 Logo 源 SVG 里 grep "#[0-9a-fA-F]{6}" 提取
#    ⚠️ 写完先过 R1–R6 六条铁律自检

# 4. 写 index.html，图片用 <figure class="img-frame contain">
#    Logo 用 <body data-logo="images/logo.svg" data-logo-position="bottom-right">

# 5. 渲染验收 + 导出（统一走 Python 脚本，别用 .bat）
PY="C:/Users/27612/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
TOOL="D:/WORK——Vie/沃克巴蒂/蜂群/蜂王/04-知识沉淀/工具/render-deck.py"

"$PY" "$TOOL" <deck>/index.html            # 出 PNG + 自动产物核对
"$PY" "$TOOL" <deck>/index.html --sheet    # 拼联系表，一屏通读验收
"$PY" "$TOOL" <deck>/index.html --pdf      # 导出 PDF（自动核对页数+比例）
"$PY" "$TOOL" <deck>/index.html --all      # PNG + PDF 一条龙
```

> **为什么弃用 `render-win.bat`**：`.bat` + cmd 在中文路径下易出编码问题；
> `render-deck.py` 全程 `pathlib` + `as_uri()`（UTF-8 安全），
> 且**强制做产物核对**（成功数 / 未生成页 / 体积偏小页），杜绝「静默零产出」。

## 疑难诊断工具

遇到「**计算样式看起来全对，但渲染不对**」时，**不要读 CSS 猜**，直接上探针：

```html
<!-- 加到待查页面 </body> 之前 -->
<script src="D:/WORK——Vie/沃克巴蒂/蜂群/蜂王/04-知识沉淀/工具/probe-box.js"
        data-probe=".deck,.slide,.dv-wrap"></script>
```

用 Chrome 截图后读左上角黄框，会输出每个元素的：
`rect`（真实渲染尺寸）/ `css`（声明值）/ `overflow` / `transform`，
并**自动扫描「疑似塌陷」的满幅层**（高度 < 父层 50% 即告警）。

## 简装模式 · 零依赖封装（2026-09-18 碗香单沉淀 + 当日扩版）

**什么时候用**：主人说「简单封装」「不要全案那套」——只要把一堆素材装订成册给人看。

**三种规格**（按素材量与展示诉求选，**先问主人**）：

| | 极简总览 | 一案一页（比稿首选） | **一案一图一文**（成品首选） |
|---|---|---|---|
| 页数 | 3–5 页 | 素材数 + 3（封面 / 索引 / 尾页） | 素材数 + 3 |
| 单个素材 | 索引页缩略图（约 280×250） | **独占一页，放大至 718–1096** | 独占一页，718–992 |
| 信息标注 | 仅序号 | 序号 + 形态名称 + 源文件规格（尺寸/格式/通道） | 同左 |
| 出图区 | 直接贴页面 | 固定尺寸**图台**（白衬底 + 1px 细线 + 轻投影） | 图台 + **右侧说明栏** |
| 文案 | 无 | 无 | **每页一段设计说明，约 120–160 字** |
| 版式 | 网格平铺 | 上图下文 | **左图右文**（图 1096 + 文 584） |

> 主人说「简单封装」→ 极简总览；说「每张单独成页 / 一案一页」→ 一案一页；
> 说「每版配一段设计说明 / 图文同页」→ **一案一图一文**。
> 2026-09-18 碗香单三级演进：3 页总览 → 14 页单页 → **14 页图文同页**。
> 一级比一级重，**改版前先确认主人要哪一档**，别自作主张加文案。

| | 全案模式 | 简装模式（两种规格通用） |
|---|---|---|
| 页数 | 20–40 页 | 3–5 页 ／ 素材数+3 |
| 结构 | 封面 / 序言 / 目录 / 章节分隔页 / 应用清单 / 尾页 | 封面 + 内容 + 尾页 |
| 页眉页脚 | 完整母版（细线 + 竖排边款 + 朱砂印 + 页码） | 一条细线 + 两端小字 |
| 依赖 | 引 html-ppt 的 `assets/` 底座 | **零依赖**（自带 CSS，不联网、不引 skill 目录） |
| 主题 | `theme-*.css` + 覆盖 swiss-grid 背景网格 | 单文件自写，约 250 行 |

**骨架（可直接复制改造）**：

```css
.stage{ position:fixed; inset:0; display:flex; align-items:center; justify-content:center; }
.deck{ position:relative; width:1920px; height:1080px; transform:scale(var(--z,1)); }

@media screen{
  .slide{ position:absolute; inset:0; width:100%; height:100%; opacity:0; }  /* R1：写死 height */
  .slide.is-active{ opacity:1; }
}
@media print{
  @page{ size:1920px 1080px; margin:0; }                                     /* R4 */
  .stage{ position:static; display:block; }
  .deck{ width:auto; height:auto; transform:none !important; }
  .slide{ position:relative !important; width:1920px !important; height:1080px !important;
          opacity:1 !important; overflow:hidden !important;   /* 必须！否则溢出的内容会分页 */
          page-break-after:always; }
  .slide:last-child{ page-break-after:auto; }
}
```

翻页用约 20 行原生 JS 读 `location.hash`（`#/2`），**不引 runtime.js**。
这套「屏幕翻页 + 打印分页」双模已实测：PDF 页数、MediaBox 比例全部正确。

**七条硬要求**（都是踩出来的）：
1. 网格项必须 `figure{margin:0}` —— UA 默认 `margin:1em 40px` 会静默掉列
2. 图片统一给 `background:#FEFDFB` 衬底 + 轻投影，**透明 PNG 与白底图观感才统一**
3. **固定画布下尺寸一律硬编码 px** —— 图片写 `max-height:100%` 时，若容器高度由 flex/stretch 推导，Chrome 会拒解该百分比、退回 auto → 图片按**原始尺寸**渲染并溢出。实测：1254px 的图在 1200px 图台里裸奔被裁，PDF 里甚至整张不画
4. **print 里必须补 `overflow:hidden !important`** —— 缺了它，任何溢出 1080px 画布的元素都会挤出一页，**PDF 页数 = slide 数 + 1**（末页近空白）
5. **导出后核 `PDF 页数 == slide 数`** —— 这是抓第 4 条的唯一手段
6. **批量插入 / 替换脚本的收尾复核必须双向** ——
   既数**新标记**（应加上的，如 `op-body`=11），**也数旧标记**（应保留的，如 `art-box`=11）。
   只验新增项会漏掉「包裹层被吃掉」这类结构性损坏：实测 `.art-box` 被正则连带删除后**图片裸奔、尺寸规则整条失效**，
   而三个新 class **全部 = 11**，复核看着"很完整" —— 假通行证
7. **DOM 测量前先摘掉祖先 transform** ——
   ```js
   deck.style.transform = 'none';                          // 改完直接读，会自动 reflow
   var w = img.getBoundingClientRect().width;               // 这时才是 1:1 布局真值
   ```
   带 `scale()` 的 deck 会让 `getBoundingClientRect()` 返回值经"缩放→除回"两次量化，
   实测偏大 6px（**724 vs 设计值 718**）；摘掉 transform 后精确得 **718.0**

**版式规格 A · 一案一页**（1920×1080，可直接照抄）：

```
主区      top 88px → bottom 80px，左右版心 88px   → 1744 × 912
信息行    高 60px  左：编号(40px 朱红) + 朱红短线 + 名称(23px 宋体)   右：源文件规格(13px)
图台      1200 × 822，内边距 52px，白衬底 + 1px 细线 + 轻投影
图片上限  max-width 1096px / max-height 718px（contain 居中，绝不裁切）
```

**版式规格 B · 一案一图一文**（左图右文，2026-09-18 扩版实测）：

```
主区      top 88px → bottom 80px，左右版心 88px   → 1744 × 912
信息行    高 60px  （同规格 A）
主区体    高 822px（= 912 − 60 − 30），左图右文横向排列，间距 64px
图台      1096 × 822，内边距 52px  →  图片上限 max-width 992 / max-height 718
说明栏    宽 584px（= 1744 − 1096 − 64），文字块垂直居中
          ├ 小标题「设计思路」15px 朱红 + 字距 .32em + 28px 前置短线
          └ 正文 18px 思源宋体 / 行高 2.05 / 两端对齐 / 色 #6E6157
```

**为什么文字块垂直居中**：图台是实心方块、占满整栏高度；文字若顶对齐，
上下留白不均会显得「上重下空」。居中后左右两栏的视觉重心落在同一条水平线上。

**设计说明怎么写**：**逐张看过图再写**，不套模板。每段 120–160 字，收在三点 ——
① 形态与构成（圆 / 匾 / 环带 / 人物 / 印章 / 笔触）
② 为什么这么做（色彩指向什么、姿态传达什么、留白为何必要）
③ 落在什么场景（头像 / 店招 / 菜单 / 礼盒 / 物料）
只写图里**确实存在**的元素，不用「高端大气」这类无信息量词，**11 段不许写成同一套话术**——
各版的价值恰在差异。图内实际用词照抄，**不"修正"原图**（碗香单里 02 图作「剔骨小炒鸡」、
10/11 图作「小炒剔骨鸡」、11 环带作「鲜炒贵州味」，三处异文均如实保留）。

**为什么图台固定尺寸**：素材形态常常差异极大（方形 / 竖版 / 横版 / 宽横混在一起），
图台固定 → 翻页时框体不动、只有画面大小变化，观感最稳；留白由 contain 自然产生。

**参考实现**：`D:\WORK——Vie\贵州遵义\碗香\Logo封装\01-工蜂产出\`
（**一案一图一文 14 页** · 11 张 Logo · 零依赖 · `theme-wanxiang.css`，换品牌只改顶部色值。
同目录下 `00-任务图.md` §7-2 有 11 段说明的撰写口径与纪律）

## 与蜂群产线的接口

```
主人出图 → [W3 图片施工蜂] 素材整理
         → html-ppt-studio 润色/排版/封装（自建主题须过 R1–R6）
         → render-deck.py 出 PDF（自动产物核对）
         → [W4 守卫蜂] G3 出厂六项验收
```

**铁律**：`image-*` 版式只用于**承载**氛围图/空间照/物料图。**Logo/标识类必须走 `vector-logo-maker` 矢量精绘**，不许用本 skill 的占位或生图逻辑。

## 参考实例

| 实例 | 路径 | 价值 |
|---|---|---|
| 梅湖小院 5 页验证 deck | `03-任务档案/20260915-HTML-PPT链路验证/01-工蜂产出/` | 最小可用样板（含 `theme-brand.css`） |
| **土蚝小院 29 页完整提案** | `E:\唐V-work\土蚝小院\品牌VI提案\01-工蜂产出\` | **全案模式完整案例：双轨封装 + 自建东方美学主题 + 29 页 + PDF 交付**（含 `theme-tuhao.css`，R1/R2 实战修复都在里面） |
| **碗香 LOGO 11 案 · 一案一页 14 页** | `D:\WORK——Vie\贵州遵义\碗香\Logo封装\01-工蜂产出\` | **简装模式（一案一页）完整案例：零依赖 · 14 页 · 11 张 Logo 各占一页 · 固定图台 + 规格标注**（含 `theme-wanxiang.css`，换品牌只改顶部色值；R1/R2 + 硬编码尺寸 + print overflow 的实战修复都在里面） |
