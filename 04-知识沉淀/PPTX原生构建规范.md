# PPTX 原生构建规范

> **产线定位**：当主人要的是 **`.ppt` / `.pptx` 文件**，而不是 PDF 或 HTML deck 时走这条线。
>
> 母版两条产线的分工：
>
> | 交付物 | 产线 | 产物特性 |
> |---|---|---|
> | PDF / 打印稿 | `VI-Proposal-Master` (HTML+CSS) → `render-deck.py` | 像素级还原，不可编辑 |
> | **`.pptx`** | **`04-知识沉淀/工具/deck2pptx.py`（python-pptx 原生构建）** | **真文本 / 真图片 / 真色块，客户可改** |
>
> **为什么不用"HTML 渲染成图再塞进 pptx"**：那样每页只是一张满幅图，客户改不了错别字。
> pptx 存在的意义就是可编辑，所以必须**原生构建**。

---

## 1. 核心换算（一次记住，全单通用）

母版画布是 **1360×850 px（16:10）**，PPT 用 EMU 作长度单位：

| 换算 | 公式 | 说明 |
|---|---|---|
| **px → EMU** | `EMU = px × 9525` | 96 dpi 下 1px = 9525 EMU。**母版所有 px 值可 1:1 直落** |
| **px → pt（字号）** | `pt = px × 0.75` | CSS 62px 标题 → PPT 46.5pt |
| **画布** | `1360×850 px → 12954000 × 8096250 EMU` | `prs.slide_width/height` |
| **字距 letter-spacing** | `spc = px × 0.75 × em × 100` | `rPr.set('spc', …)`，单位 1/100 pt |
| **行距 line-height** | `line_spacing = css_lh / 1.2` | PPT 单倍行距≈1.2×字号，故要除 1.2 才能对齐 CSS |

```python
PXU = 9525
def E(v): return Emu(int(round(v * PXU)))

prs = Presentation()
prs.slide_width  = E(1360)
prs.slide_height = E(850)
slide = prs.slides.add_slide(prs.slide_layouts[6])   # 6 = 空白版式
```

## 2. 母版几何常量（直接抄）

```python
W, H = 1360, 850
MX   = W * 0.11      # 149.6  左右边距 11%
HDR  = H * 0.15      # 127.5  页眉带高 15%
CW   = W - 2 * MX    # 1060.8 版心宽
```

- 页眉：左侧标题 + 伸缩细线 + 右侧英文，**垂直居中于 0 ~ HDR 之间**（中线 63.75）
- 内容区：`top = HDR`，`bottom = H`，**内容整体垂直居中**
- **不设页码**

### 页眉细线的正确定位

线的起止要按**实测文字宽度**算，不能估：

```python
# 用 PIL 量文字像素宽，再定位线的两端
ImageFont.truetype(r'C:\Windows\Fonts\msyhbd.ttc', 100).getlength(text) * size_px / 100

x1 = MX + 左文字宽 + 30
x2 = (W - MX - 右文字宽) - 30
# 线用极扁矩形；页眉线设计粗 1.5px，实测渲染 1.33px，正常
rect(slide, x1, HDR/2 - 0.75, x2 - x1, 1.5, color)
```

## 3. 中文字体（**最大的坑**）

`run.font.name` 只写 `a:latin`，**对中文字符无效**——中文走 `a:ea`（东亚字体）槽位。
不写 `a:ea` 就会回退宋体。

```python
from pptx.oxml.ns import qn

r = p.add_run(); r.text = s
r.font.name = fam            # 只影响拉丁字符
rPr = r._r.get_or_add_rPr()
ea = rPr.find(qn('a:ea'))
if ea is None:
    ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
ea.set('typeface', fam)      # ← 中文字体必须补这一句
```

**字体选型**（本机实测已装，见下表）：

| 用途 | 声明字体 | 理由 |
|---|---|---|
| 中文正文/标题 | `Microsoft YaHei` | Windows 通用，客户机不会掉字 |
| 英文/数字 | `Arial` | 同上 |
| 等宽（HEX 色值） | `Consolas` | 同上 |
| 衬线（徽章/尾页） | `SimSun` | 同上 |

> 母版 CSS 用 `Source Han Sans SC`，本机对应 **`Noto Sans SC`**（已装）。但客户机大概率没有，
> 除非明确要求，**默认用 `Microsoft YaHei` 保兼容**。

## 4. 版式件配方

### 4.1 文本框三件套

```python
tb = slide.shapes.add_textbox(E(x), E(y), E(w), E(h))
tf = tb.text_frame
tf.word_wrap = True
tf.auto_size = MSO_AUTO_SIZE.NONE
tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
tf.vertical_anchor = MSO_ANCHOR.MIDDLE     # 单行用 MIDDLE，多行段落用 TOP
```

还须给每个段落清掉默认间距：`p.space_before = Pt(0)`、`p.space_after = Pt(0)`。

### 4.2 形状要去阴影

`add_shape` 会继承主题阴影，必须关掉：

```python
s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, E(x), E(y), E(w), E(h))
s.fill.solid(); s.fill.fore_color.rgb = RGBColor.from_string(hex)
s.line.fill.background()      # 无描边
s.shadow.inherit = False      # 关阴影
```

### 4.3 图片：等比适配 + 居中，绝不拉伸

```python
def picture(slide, path, bx, by, bw, bh):
    with Image.open(path) as im: iw, ih = im.size
    r = min(bw / iw, bh / ih)            # contain，不裁不拉
    w, h = iw * r, ih * r
    slide.shapes.add_picture(path, E(bx + (bw-w)/2), E(by + (bh-h)/2), E(w), E(h))
```

> 同一张图重复插入**不会**让文件膨胀——python-pptx 按 SHA1 去重 ImagePart。
> 本轮 14 页里 logo-壹 出现 4 次，pptx 仍只有 3.27MB。

### 4.4 常用页型落位（本轮实测值，可直接复刻）

| 页型 | 关键坐标（画布 px） |
|---|---|
| 封面 | 主色底；主标题 y246 h112 / 副题 y370 / 英文 y432 / meta y476 / 色块标签 y536 |
| 章节隔断 | 圆环 292×292 居中于内容区（y 342.75）；胶囊色块居中压在环心上 |
| 单件居中图 | 图框 `(MX, 154, CW, 620)`，说明 y796、副说明 y824 |
| 左图右文 | 左图框 `(MX, 254, 613, 470)`；右栏 `x = MX+665`，宽 395.6；3 组 × 128 行距 |
| 三格网格 | `gw = (CW-44)/3 = 338.93`，间隙 22；图台 y283，tag y642，说明 y705 |
| 五色卡 | 格宽 `CW/5 = 212.16`，y275 高 380；格内文字自底倒推：名 y-96 / HEX y-68 / 角色 y-40 |
| 比例条 | y293 高 110，按百分比横向累加切块 |
| 尾页 | 主色底；签名 `(MX, 52)`；`Thanks!` 宋体 112px 垂直居中 |

### 4.5 三套可复用版式模板（碗香「三方案展示」5 页册实测值）

**① 一案一图一文 + 色彩同页**（标志详页）

```
左：标志展示台  rect(MX, 158, 560, 442) 填 FAF7F2
    图片内缩 34 → contain 于 492×374（近方图实际落在 374 高左右）
右：rx = MX + 560 + 60.4 = 770，rw = 440.4
    红线 56×3 @ y158
    「标志构成」25 bold @ y176（anchor=m）
    三段：y 从 244 起，节奏 120px/段
          段标题 18 bold BRAND_D（框高 28，anchor=m）
          段正文 15 INK2 lh1.62 两端对齐（框高给 80）
          ⚠️ 曾用 lh1.9 + 段步进 119 → 段占 119.5，**段间距 −0.5px**，三段粘连成一坨
下：分隔线 y630
    「色彩应用」21 bold + 右侧来源说明 13（右对齐）
    色卡 4 等宽块 (CW-60)/4 @ y686 高 66
      块内：名称 14 bold @ y+13 · HEX 12 mono @ y+35
    配比条 y762 高 22，按 % 分宽，段内右对齐标 %
      段宽 < 72px 不标百分比（会溢出）
    底注 13 INK2 @ y800（写各色角色分工，比塞进色块更省空间）
```

- **色卡文字色按底色明度选**：浅底（`F7E4CE` / `EBDBC8` / `F0E2D7` / `F28856`）用 INK，深底用 PAPER。
- **色值 + 配比分离表达**：上排等宽色卡承载"色值"，下排按比例分宽承载"用量"——比"色块按比例排布 + 块内塞三层文字"清楚得多。

**② 三版并置页**

```
gw = (CW - 2*36)/3 = 329.6，间距 36
图台 rect(x, 236, gw, 414) 填 FAF7F2，图片内缩 26
标签：编号 15 bold BRAND spc .20 @ y668
      名称 19 bold INK @ y694
      定位 13 INK2 @ y726
底：分隔线 y770 + 一句总结 @ y786
```

> **并排等大的判据是"内容宽度"，不是"框宽"。** 本轮三版源图内容比例 0.991 / 0.968 / 0.986（近方），
> contain 后全部按宽度占满 → 视觉自然等大。若比例差异大，必须显式统一内容宽度。

**③ 应用载体示意页（矢量绘制，非实拍 mockup）**

| 载体 | 画法 | 用稿 |
|---|---|---|
| 门头灯箱 | 墙面 rect + 深色招牌 rect + logo + 门洞（居中 + 双开缝）+ 两盏对称壁灯 | 反白稿 |
| 外带碗盖 | 浅底 + 双环圆（外白描边 / 内米）+ 彩色 logo + 右侧规格文字 | 彩色稿 |
| 餐具烙印 | 浅底 + 圆角矩形木牌（radius 0.06）+ 3 条木纹线 + 墨稿 | 单色墨稿 |
| 员工围裙 | 深底 + 围裙片 + 两条肩带 + logo | 反白稿 |
| 名片 | 浅底 + **左右并排双卡**（白卡彩稿 / 主色卡反白稿） | 彩 + 反白 |

- 每个载体下方两行标签：主名 14 bold + 用稿说明 12.5 INK2。
- **深底载体必须用反白稿，木色/暖底用墨稿或彩稿**——判错会出现"看不见的标志"。
- 木纹线要**先画线后画 logo**，线自然被 logo 遮住，不必逐条算避让。
- **不要重叠叠放双卡**：后卡会遮掉前卡大片面积，视觉上像"残卡"。并排最稳。

**④ 母版已固化（优先直接用，别再手搭）**

`04-知识沉淀\母版\Logo-Scheme-Show-Master\` — README.md 有三步用法。
附 `gen_instance.py`：把母版配置区换成新单路径，生成实例脚本 —— **维护只有母版一处**。
两单实测通过（碗香「一」v2 / 「二」）。

---

## 5. 验收方法（**别信工具报的 bbox**）

标准链路：

```
pptx  ──LibreOffice──▶  PDF  ──PyMuPDF 渲染──▶  PNG  ──PIL 像素扫描──▶  实测值
         headless                                                        ↓
                        联系表通读（整体）                          与设计值比对
```

```bash
"/c/Program Files/LibreOffice/program/soffice.exe" --headless --norestore \
  -env:UserInstallation=file:///C:/temp/lo_bee \
  --convert-to pdf --outdir "C:/temp/wxppt" "<deck.pptx>"
```

> ⚠️ `-env:UserInstallation` 必须指向**纯 ASCII 临时目录**（见踩坑库「中文路径」条）。

### 5.1 ⛔ 不要用 `page.get_image_info()` 的 bbox 判几何

它返回渲染对象的**外接框**，含描边与抗锯齿过渡带，本轮系统性**外扩约 4.2px**。
本轮据此误判了两处"事故"，实际全对。

### 5.2 ✅ 用像素扫描，且**先定位行位再扫边界**

```python
im = Image.open(png).convert('L'); W, H = im.size
sx = W / 1360.0                      # 渲染缩放比

# 第一步：大阈值扫全页，定位元素真实 y（行距会让文字整体下移约 19px，别拿设计坐标当扫描坐标）
for yy in range(0, H, 4):
    cnt = sum(1 for xx in range(0, W, 2) if im.getpixel((xx, yy)) < 200)
    if cnt: print(yy / sx, cnt)

# 第二步：在文字行上精扫横向边界（或找色块的色彩突变点）
xs = [xx for xx in range(W) if im.getpixel((xx, y)) < 190]
print(xs[0] / sx, xs[-1] / sx)
```

**扫描点落在行距空隙上会"扫个空"**，得出"这里没内容"的错误结论——本轮踩过一次。

### 5.3 收尾必核产物

跑外部程序产出文件的命令，**收尾必须数数量 + 看体积**：

```bash
ls -la /c/temp/wxppt/          # PDF 是否生成
# PyMuPDF 核页数 == slide 数；核 MediaBox 比例 == 16:10
```

---

## 6. 标志素材加工（VI 单必备前置）

AI 生成的 logo 图通常是**白底不透明 RGBA**，做反白/深底场景前必须去背。

| 需求 | 做法 |
|---|---|
| **去白底** | **四角洪水填充**：`ImageDraw.floodfill(im, 角, (0,0,0,0), thresh=42)`，四个角各来一次。只吃连通到边框的白，**内部白（白袍/牙齿/头巾）完整保留** |
| 灰阶稿 | `ImageOps.grayscale` + 保留原 alpha，合成 RGBA |
| 单色墨稿 | 灰阶再 `point(lambda v: 0 if v<128 else 255)` |
| **反白稿** | **双色互换**：按亮度二值化，**暗部 → 白、亮部 → 本版主色**（RGB 重映射，原 alpha 不变）。⛔ **不可**把可见像素全涂白——那只会得到一坨**无结构的纯白剪影**，门头/围裙/名片上全部废掉（见踩坑库） |
| 色值提取 | 严格条件 + **众数**，勿用中位数/均值——会被肤色、渐变污染。本轮：`r>=150 and g<=95 and b<=95 and r-g>=75` |
| **改完必须复核** | 把去背图**合成到深底**上目视——查残留白边、查内部白有没有被挖穿 |

### 6.1 去背后必做一步：裁掉透明边（trim）

```python
im = Image.open(p).convert('RGBA')
al = im.split()[3].point(lambda v: 255 if v > 12 else 0)   # 阈值滤掉抗锯齿
bb = al.getbbox()
im.crop(bb).save(out)
```

**为什么必做**：原图（尤其 1536×1024 横构图）自带大片透明边，不 trim 就 contain 进框，
实际内容只占框宽六成左右——**多版并排时大小明显不一，看着像做坏了**。

本轮实测：trim 后三版内容比例 0.991 / 0.968 / 0.986，全部近方，并排自然等大。

---

## 7. 交付惯例

```
<品牌>-<册名>\
├── 00-任务图.md
├── 01-工蜂产出\
│   ├── <品牌>-<册名>.pptx        ★ 主交付
│   ├── <品牌>-<册名>.pdf         ← 预览（LibreOffice 转）
│   └── 标志衍生素材\             ← 去背/灰阶/单色墨/反白，各形态齐备
└── 02-验收单.md
```

- 主人说 `.ppt` 一般泛指 PPT 文件，**交付 `.pptx`**；确需 97-2003 格式时说明另存即可。
- **不自动 commit / push**（见 `~/.workbuddy/MEMORY.md` 第 6 条）。

---

## 8. 参考实现

- **母版（优先用，别再手搭）**：`04-知识沉淀\母版\Logo-Scheme-Show-Master\`
  `prep-assets.py`（素材加工）+ `build.py`（版式构建）+ `gen_instance.py`（生成实例）+ `README.md`
- 首单 14 页基础系统 + 追加 5 页三方案展示：`碗香\Logo一-全案封装\`
  - `_work\build_pptx.py`（14 页：封面/序言/章节/形象/释义/黑白稿/色彩/字体）
  - `_work\build_show.py`（5 页 · §4.5 版式模板的来源）
  - `_work\probe_show.py`（**pptx 内图片宽高比零变形探针**，比 PDF 探针更直接）
- 二单（母版首次复用 + 两处缺陷修正）：`碗香\Logo二-全案封装\`
  - `_work\prep2.py`（含反白稿修正）· `_work\build_show2.py` · `_work\fitcheck.py`（色卡与配比条像素核对）
- 通用探针工具：`04-知识沉淀/工具/probe-pptx.py`（输入任意 pptx，报每张图失配数）
- 骨架模板：`04-知识沉淀/工具/deck2pptx.py`
- 全案母版：`04-知识沉淀/母版/VI-Proposal-Master/`（HTML/CSS 版，几何同源）
