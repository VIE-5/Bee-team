# html-ppt-studio 使用手册（Windows）

> 引入日期：2026-09-15 ｜ 来源：https://github.com/lewislulu/html-ppt-skill ｜ 许可：MIT
> 安装位置：`C:\Users\27612\.workbuddy\skills\html-ppt`

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

## ⚠️ Windows 上的三个坑（原版未覆盖）

### 坑 1：`scripts/render.sh` 是 macOS 专用
Chrome 路径写死 `/Applications/Google Chrome.app/...`，Windows 直接报 `Chrome not found`。
**解法**：用 `04-知识沉淀/工具/render-win.bat` 替代。

### 坑 2：Chrome headless 必须带 `--user-data-dir`
不带独立 profile 会**静默失败**（退出码 0 但零文件写出）。
**解法**：`--user-data-dir=<临时目录>`，且用完 `rmdir` 清理（否则一次测试就占 40M）。

### 坑 3：跨盘符时资源路径算歪
`new-deck.sh` 的 `relpath()` 在 D 盘 deck + C 盘 skill 时，算出 `../../../../../../../../c/Users/...` 这种畸形路径。
**解法**：deck 建在 skill 目录内（如 `examples/`），或在同盘符下工作。

### 附加坑：README 承诺的部分文件不存在
README 提到 `scripts/export-pdf.sh`，**仓库里实际没有**。PDF 得自己用 Chrome `--print-to-pdf` 出。

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

# 4. 写 index.html，图片用 <figure class="img-frame contain">
#    Logo 用 <body data-logo="images/logo.svg" data-logo-position="bottom-right">

# 5. 渲染验收
render-win.bat <deck>/index.html 5      # 出 PNG 逐张肉眼验收
render-win.bat <deck>/index.html pdf    # 出 PDF 交付
```

## 与蜂群产线的接口

```
主人出图 → [W3 图片施工蜂] 素材整理
         → html-ppt-studio 润色/排版/封装
         → render-win.bat 出 PDF
         → [W4 守卫蜂] G3 出厂六项验收
```

**铁律**：`image-*` 版式只用于**承载**氛围图/空间照/物料图。**Logo/标识类必须走 `vector-logo-maker` 矢量精绘**，不许用本 skill 的占位或生图逻辑。

## 参考实例
`03-任务档案/20260915-HTML-PPT链路验证/01-工蜂产出/` —— 梅湖小院 VI 提案 5 页验证 deck
（含 `theme-brand.css` 品牌主题，可直接复制改造）
