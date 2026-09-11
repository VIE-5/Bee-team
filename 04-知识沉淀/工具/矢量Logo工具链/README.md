# 矢量 Logo 工具链

标识/Logo 类任务的完整产线工具。**生图通道不能做标识**，原因见 `04-知识沉淀/踩坑库.md`（2026-09-11 整单退回事件）。

## 三步走

```bash
cd <任务目录> && NODE_PATH="$HOME/.workbuddy/binaries/node/workspace/node_modules" \
  "<node-dir>/node.exe" svg2png.js "./src" "./png"     # ① SVG → 多尺寸透明 PNG
"<venv>/python.exe" make-sheet.py <子目录> "a,b,c"      # ② 多候选拼比稿图（一次看清）
"<venv>/python.exe" make-board.py                       # ③ 单色/反白/提案展板
```

## 依赖安装

```bash
mkdir -p ~/.workbuddy/binaries/node/workspace && cd "$_"
"<node-dir>/npm.cmd" init -y
"<node-dir>/npm.cmd" install @resvg/resvg-js --no-audit --no-fund
```

Python 侧只需 Pillow（装在本环境隔离 venv 里）。

## 中文字体（全部 SIL OFL 1.1，免费可商用）

用 PIL 渲染字标前需下载。**注意：变体字体（`xxx[wght].ttf`）在 Pillow 12 + 当前 FreeType 下无法读取变体轴，会直接渲染失败——必须用静态实例。**

已实测可用的直链：

| 字体 | 直链 | 大小 |
|---|---|---|
| 思源黑体 Light | `https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/Sans/SubsetOTF/SC/NotoSansSC-Light.otf` | 8.3M |
| 思源黑体 Regular | `https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/Sans/SubsetOTF/SC/NotoSansSC-Regular.otf` | — |
| 思源宋体 Light | `https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/Serif/SubsetOTF/SC/NotoSerifSC-Light.otf` | 11.5M |
| 马善政楷书 | `https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/mashanzheng/MaShanZheng-Regular.ttf` | 5.6M |
| 站酷小薇 | `https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/zcoolxiaowei/ZCOOLXiaoWei-Regular.ttf` | 6.1M |

**已踩的坑**：
- `ofl/notoserifsc/NotoSerifSC[wght].ttf` → jsDelivr 返回 403
- `ofl/ibmplexsanssc/*` → 404（不在 google/fonts 仓库）
- **Zen Kaku Gothic New 缺简体汉字**（日语字体），`烧`/`鱼` 直接缺字 → 中文任务不可用
- 字体缓存目录：`~/.workbuddy/binaries/node/workspace/_fonts/`

## 文件

| 文件 | 作用 |
|---|---|
| `svg2png.js` | SVG → PNG 1024/512/256/96（透明底） |
| `make-sheet.py` | 多候选横向拼成一张比稿图（省 context） |
| `make-board.py` | 生成单色版 / 反白版 / 提案展板 |
| `lockup.py` | 生成中文字标锁定版（横式/竖式）+ 组合规范板 |

## 硬指标自检（不达标不算 Logo）

纯平涂零渐变 · 可单色 · 32px 可辨 · 真矢量可缩放 · 图形凝练（能被平铺复用的 = 辅助图案，不合格）
