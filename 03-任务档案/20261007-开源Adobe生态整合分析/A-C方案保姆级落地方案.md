# 从零到「A 加装 + C 外挂」保姆级落地方案

> **适用机型**：i5-10400 / 16GB 内存 / Intel UHD 630 核显 / Win11 专业版
> **撰写时间**：2026-10-07
> **前置结论**：主人机器**无独立显卡** → 本地大模型生图（ComfyUI+FLUX）**不可行**；矢量工具链**完全不受影响**。
> **命名对齐**：本文中 **「A 加装」= 给矢量工具装自动化脚本/插件**；**「C 外挂」= 本地 AI 图像工具链（轻量版）**。

---

## 〇、先看清主人的机器底细（实测）

| 项目 | 实测值 | 判定 |
|---|---|---|
| CPU | Intel i5-10400（6核12线程 @2.9GHz） | ✅ 够用 |
| 内存 | 15.8GB（**当前空闲仅 3.5GB**） | ⚠ 偏紧，装前先关软件 |
| 显卡 | **Intel UHD 630 核显**（无独显） | ❌ **ComfyUI/FLUX 出局** |
| C 盘 | 总 100GB，**仅剩 15.4GB** | 🚨 **绝不可装这里** |
| D 盘 | 总 183GB，**剩 124.1GB** | ✅ **主安装盘** |
| E 盘 | 总 182GB，剩 45.4GB | 备用 |
| 已装设计软件 | 无 | 全新安装 |

### 配置对方案的三条硬约束

1. **不装 ComfyUI**：核显跑 diffusion 模型，一张图要等十几分钟且极易爆内存 → 改用**轻量本地 AI**（抠图/修图/放大）+ 云端生图补充。
2. **全部装 D 盘**：C 盘只剩 15GB，装完 Adobe 级软件必爆盘。
3. **装前清内存**：当前空闲仅 3.5GB，安装过程建议关闭浏览器等吃内存程序。

---

## 一、方案总览（A 加装 + C 外挂）

```
                    ┌─────────────────────────────┐
   【主链】矢量设计   │  Inkscape 1.4.4  ← 替代 Illustrator  │
                    └───────────┬─────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        │                                               │
   【A 加装】                                       【C 外挂】
   给 Inkscape 装自动化                           本地 AI 图像工具链
   ├─ 命令行批量导出 (PNG/PDF)                    ├─ rembg    抠图（MIT）
   ├─ Python 扩展 (inkex)                        ├─ IOPaint  去水印/外扩
   └─ 第三方扩展库                                └─ Upscayl  放大
                                                    │
        ┌───────────────────────────────────────────┘
        │
   【辅助】位图编辑：Krita 5.3.4 / GIMP 3.2.4
```

| 层级 | 工具 | 版本 | 许可 | 免费 | 装哪 |
|---|---|---|---|---|---|
| 矢量主力 | **Inkscape** | 1.4.4 | GPL-2.0+ | ✅ | D 盘 |
| 位图/绘画 | **Krita** | 5.3.4 | GPL-3.0 | ✅ | D 盘 |
| 位图/修图 | **GIMP** | 3.2.4 | GPL-3.0+ | ✅ | D 盘 |
| 抠图 | rembg | 最新 | **MIT** | ✅ | D 盘 |
| 修图/去水印 | IOPaint | 最新 | Apache-2.0 | ✅ | D 盘 |
| 放大 | Upscayl | 最新 | AGPL-3.0 | ✅ | D 盘 |

> **全部零成本、可商用**（自用/内部/交付成品均不触发 copyleft 条款）。

---

## 二、第 0 步：安装前准备（5 分钟）

### 2.1 建目录（一次性）

打开 **PowerShell**（Win+X → 终端），粘贴运行：

```powershell
New-Item -ItemType Directory -Force -Path "D:\DesignTools" | Out-Null
New-Item -ItemType Directory -Force -Path "D:\DesignTools\Installers" | Out-Null
New-Item -ItemType Directory -Force -Path "D:\DesignTools\Projects" | Out-Null
Write-Output "目录已建好：D:\DesignTools"
```

### 2.2 关闭吃内存的程序

当前空闲内存仅 3.5GB，安装期间请关掉浏览器多余标签页。

### 2.3 下载文件统一放这里

所有安装包下载到 `D:\DesignTools\Installers`，装完可删。

---

## 三、主链：Inkscape 安装（替代 Illustrator）

> Inkscape 是开源世界最成熟的矢量工具，**原生 SVG 格式**，与主人的「矢量精绘 Logo」铁律完美契合。

### 3.1 下载

- **官方地址**：https://inkscape.org/release/
- **直链（Windows 64位）**：https://inkscape.org/gallery/item/61284/inkscape-1.4.4_2026-05-05_dcaf3e7-x64.signed.exe
- ⚠️ **务必从 inkscape.org 官网下载**，搜索引擎上的仿冒站可能夹带垃圾软件。

**文件名参考**：`inkscape-1.4.4_2026-05-05_dcaf3e7-x64.signed.exe`（约 162MB）
**SHA256 校验**（可选，验证完整性）：下载页有 `.sig` 签名文件。

### 3.2 安装（关键：改路径到 D 盘）

1. 双击 `inkscape-1.4.4-...-x64.signed.exe`
2. 语言选「**简体中文**」→ 确定
3. 一路「下一步」，到**选择安装位置**时：
   - **务必改成** `D:\DesignTools\Inkscape`
   - ❌ **不要**用默认的 `C:\Program Files\Inkscape`（C 盘没空间）
4. **勾选**「Add Inkscape to the system PATH for all users」（**重要！A 加装靠这个**）
   - 如果没勾，命令行批量导出用不了
5. 组件全选（默认即可）→ 安装 → 完成

### 3.3 验证安装

新开一个 PowerShell，粘贴：

```powershell
& "D:\DesignTools\Inkscape\bin\inkscape.com" --version
```

**预期输出**：`Inkscape 1.4.4 (dcaf3e7, 2026-05-05)`

> 如果提示命令不存在，说明 PATH 没配好 → 用上面这条绝对路径即可，不影响使用。

### 3.4 切换中文界面（如果没自动中文）

`编辑` → `首选项` → `界面` → `语言` 选「简体中文 (zh_CN)」→ 重启。

---

## 四、A 加装：给 Inkscape 装上自动化能力

这是主人问的「A 方案」核心 —— **不换工具，给工具加能力**。

### 4.1 第一招：命令行批量导出（最实用）

**场景**：一次导出 50 个 SVG 成 PNG / PDF，手工点要 100 次。

#### 单文件导出

```powershell
# SVG → PNG（宽 1920px）
& "D:\DesignTools\Inkscape\bin\inkscape.com" "D:\DesignTools\Projects\logo.svg" --export-filename="D:\DesignTools\Projects\logo.png" --export-width=1920

# SVG → PDF（裁剪到图形边界）
& "D:\DesignTools\Inkscape\bin\inkscape.com" "D:\DesignTools\Projects\logo.svg" --export-filename="D:\DesignTools\Projects\logo.pdf" --export-area-drawing
```

#### 批量导出脚本（推荐保存复用）

新建文件 `D:\DesignTools\batch-export.ps1`，内容：

```powershell
# 批量把当前目录所有 SVG 导出为 PNG + PDF
$inkscape = "D:\DesignTools\Inkscape\bin\inkscape.com"
$dpi = 300          # 印刷用 300，网页用 96
$widthPx = 2000     # PNG 宽度

Get-ChildItem -Filter *.svg | ForEach-Object {
    $base = $_.BaseName
    Write-Output "处理: $($_.Name)"
    
    # 导出 PNG
    & $inkscape $_.FullName --export-filename="$pwd\$base.png" --export-width=$widthPx
    
    # 导出 PDF
    & $inkscape $_.FullName --export-filename="$pwd\$base.pdf" --export-area-drawing
}
Write-Output "全部完成"
```

**用法**：把 SVG 放进一个文件夹 → 在该文件夹打开 PowerShell → 运行：

```powershell
cd "D:\DesignTools\Projects\某项目"
powershell -ExecutionPolicy Bypass -File "D:\DesignTools\batch-export.ps1"
```

> ⚠️ **首次运行若被拦**，是因为 PowerShell 执行策略。上面命令里的 `-ExecutionPolicy Bypass` 就是绕过单次限制，安全。

#### 常用导出参数速查

| 参数 | 作用 | 示例 |
|---|---|---|
| `-w` / `--export-width` | 指定宽度 | `-w 1920` |
| `-h` / `--export-height` | 指定高度 | `-h 1080` |
| `-d` / `--export-dpi` | 分辨率 | `-d 300` |
| `-D` / `--export-area-drawing` | 裁剪到内容边界 | 去白边神器 |
| `-C` / `--export-area-page` | 按页面尺寸 | 保持画板 |
| `-i` / `--export-id` | 只导出某对象 | `-i logo-mark` |
| `--export-type` | 指定格式 | `png,pdf` |

### 4.2 第二招：安装第三方扩展

**找扩展**：
- 官方扩展库：https://inkscape.org/gallery/=extension/
- GitHub 搜索 `inkscape extension`

**安装步骤**：

1. Inkscape 菜单 `编辑` → `首选项` → `系统`
2. 找到「**用户扩展目录**」，点「**打开**」
   - Windows 实际路径通常是：`C:\Users\27612\AppData\Roaming\inkscape\extensions`
   - ⚠️ 这个在 C 盘，但只是小文件，没关系
3. 把扩展的 **`.inx` 和 `.py` 文件直接复制**进去（**不要**整个文件夹嵌套）
4. **重启 Inkscape** → 在 `扩展` 菜单里找

**推荐新手先用内置扩展**（无需安装）：
- `扩展` → `从路径生成` → `沿路径图案`
- `扩展` → `渲染` → `条形码` / `二维码`
- `扩展` → `修改路径` → `节点抖动`
- `扩展` → `导出` → `优化 SVG`（**发布网页必用**）

### 4.3 第三招：Python 扩展写自动化

Inkscape 自带 Python，可写扩展脚本。**进阶内容**，先跳过，等熟练了再用。

关键信息备查：
- 扩展 = 一个 `.inx`（描述界面）+ 一个 `.py`（执行逻辑）
- Inkscape 内部 Python 路径可在 `首选项 → 系统` 查到
- 核心库 `inkex` 可独立于 Inkscape 运行（`pip install inkex`）

---

## 五、C 外挂：本地 AI 图像工具链（轻量版）

> ⚠️ **重要前提**：主人无独显，**不装 ComfyUI**。以下三个工具**CPU 就能跑**，正好补足日常修图/抠图/放大。

### 5.1 rembg —— 一键抠图（★ 最推荐，MIT 许可最宽松）

**用途**：菜品图、商品图批量抠背景，**不限张数、不上传、离线**。
**硬件**：纯 CPU 可跑 ✅

#### 安装（装到 D 盘）

```powershell
# 1. 建 Python 虚拟环境（隔离，不污染系统）
cd D:\DesignTools
C:\Users\27612\.workbuddy\binaries\python\versions\3.13.12\python.exe -m venv rembg-env

# 2. 激活环境
D:\DesignTools\rembg-env\Scripts\Activate.ps1

# 3. 安装 rembg（CPU 版 + 命令行工具）
pip install "rembg[cpu,cli]"
```

> ⚠️ 如果 `Activate.ps1` 被策略拦住，改用：
> `D:\DesignTools\rembg-env\Scripts\activate.bat`（在 cmd 里跑）

#### 使用

```powershell
# 单张
rembg i "D:\图片\菜品.jpg" "D:\图片\菜品-去背.png"

# 整个文件夹批量
rembg p "D:\图片\原图" "D:\图片\去背"
```

**首次运行会下载模型**（约 170MB），之后全程离线。

#### 输出位置
生成 `-去背.png`，透明背景，可直接拖进 Inkscape 排版。

---

### 5.2 IOPaint —— 去水印 / 去路人 / 外扩画幅

**用途**：开源版「内容识别填充」，主人物料清洁、补边。
**许可**：Apache-2.0（商用友好）
**硬件**：CPU 可跑，但**较慢**（一张图约 30秒–2分钟）⚠

#### 安装

```powershell
cd D:\DesignTools
C:\Users\27612\.workbuddy\binaries\python\versions\3.13.12\python.exe -m venv iopaint-env
D:\DesignTools\iopaint-env\Scripts\Activate.ps1
pip install iopaint
```

#### 启动（本地网页界面）

```powershell
# 用 CPU 跑 LaMa 模型（去物体/水印最稳）
iopaint start --model=lama --device=cpu --port=8080
```

浏览器打开 **http://localhost:8080** → 上传图 → 涂抹要去掉的地方 → 点 Erase。

**用法**：涂抹 → 完成。支持去水印、去路人、去瑕疵。

> ⚠️ CPU 跑 diffusion 类功能（换物体）会很慢，**建议只用 LaMa 擦除模式**。

---

### 5.3 Upscayl —— AI 图片放大

**用途**：糊图、小图放大 4 倍，老照片修复。
**许可**：AGPL-3.0（**自用/内部完全没问题**）
**硬件**：核显可跑 ✅

#### 安装（桌面软件，最简单）

1. 下载：https://github.com/upscayl/upscayl/releases
2. 选 `upscayl-x.x.x-win.exe`（Windows 安装包）
3. 安装路径改成 `D:\DesignTools\Upscayl`
4. 打开软件 → 选图片 → 选模型（推荐 `upscayl-standard-4x`）→ 点 UPSCAYL

---

## 六、辅助位图工具（按需装）

### 6.1 Krita 5.3.4（数字绘画，GPL-3.0）

- **下载**：https://krita.org/en/download/ → `krita-x64-5.3.4-setup.exe`（约 158MB）
- **装到**：`D:\DesignTools\Krita`
- **用途**：插画、概念图、材质绘制；也可打开 PSD
- **注意**：不装 6.0.x 版（Qt6 迁移，稳定性待观察，官方建议生产用 5.3.x）

### 6.2 GIMP 3.2.4（位图修图，GPL-3.0+）

- **下载**：https://www.gimp.org/downloads/ → `gimp-3.2.4-setup.exe`
- **装到**：`D:\DesignTools\GIMP`
- **用途**：照片修图、合成；支持 Python-Fu 脚本
- **注意**：PSD 兼容有坑（矢量图层会丢），**别做往返编辑**

> 💡 **建议**：先装 Inkscape + rembg 就够用，Krita/GIMP 按需再说。

---

## 七、验收清单（照做即可确认成功）

### Inkscape
- [ ] PowerShell 运行 `--version` 输出 `Inkscape 1.4.4`
- [ ] 打开 Inkscape，界面是中文
- [ ] 用钢笔工具（B）画一条线，能编辑节点
- [ ] 命令行成功导出一个 PNG

### A 加装
- [ ] `batch-export.ps1` 能跑通，批量产出 PNG + PDF
- [ ] `扩展` 菜单里能看到内置扩展（如「优化 SVG」）

### C 外挂
- [ ] rembg 成功抠出一张透明背景图
- [ ] IOPaint 网页能打开（http://localhost:8080）
- [ ] Upscayl 能放大一张图

---

## 八、常见问题

| 问题 | 原因 | 解法 |
|---|---|---|
| PowerShell 说「禁止运行脚本」 | 执行策略限制 | 加 `-ExecutionPolicy Bypass` |
| `inkscape` 命令找不到 | PATH 没配 | 用绝对路径 `D:\DesignTools\Inkscape\bin\inkscape.com` |
| 导出的 PNG 模糊 | DPI 太低 | 加 `-d 300` 或用 `-w 3000` |
| 导出图周围有大片白边 | 没裁剪 | 加 `--export-area-drawing` |
| rembg 报错找不到模型 | 首次需联网下载 | 保证网络，下载后即离线 |
| IOPaint 太慢 | CPU 跑 AI | 只用 LaMa 擦除，别用 diffusion |
| C 盘又满了 | 装错位置/缓存 | 检查是否都装到 D 盘；清 `%APPDATA%\inkscape` 缓存 |

---

## 九、后续可扩展（等熟练后）

| 想做的事 | 方案 | 备注 |
|---|---|---|
| 真·AI 生图（氛围图/KV） | **云端**跑（即梦/可灵/Flux API） | 本机核显跑不动 |
| 升级硬件后 | ComfyUI 本地部署 | 需 NVIDIA 独显 ≥8GB 显存 |
| 让 AI 直接改图 | IOPaint + 蜂群 agent 调度 | 可选进阶 |
| 设计协作/版本管理 | Git + Penpot 自托管 | 主人在做 Git 流程 |

---

## 十、一句话总纲

> **Inkscape 顶替 Illustrator，A 加装用命令行批量导出 + 扩展；C 外挂走轻量本地 AI（rembg 抠图 / IOPaint 修图 / Upscayl 放大）—— 全部零成本、可商用、装 D 盘，核显机器照样跑。**
