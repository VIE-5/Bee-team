# 开源 Adobe 生态整合分析

> **检索时间**：2026-10-07
> **数据源**：GitHub 仓库页 + 第三方仓库统计（RepositoryStats / GitTrend / ToolVitals / Cataito / ToolTrust）
> **口径声明**：★ 星数为**检索当日快照**（不同统计站存在 ±5% 偏差）；许可与活跃度**落地前一律以仓库 LICENSE / 最近一次提交为准**。未取得确证的一律标 `—`，不臆断。

---

## 一、结论先行

GitHub 上「开源 Adobe」不是一个东西，而是**三条互不冲突的路线**：

| 路线 | 一句话 | 成熟度 | 对主人的价值 |
|---|---|---|---|
| **A 加装** | 不换软件，用开源脚本 / MCP 给 PS·AI·ID 装上自动化与 AI 能力 | 高（立刻可用） | 把批量导出 / 改名 / 图层 / 规格表等重复劳动自动化；让 AI 直连 PS |
| **B 替换** | 用 GIMP / Inkscape / Krita / Penpot 等替换 Adobe 订阅 | 中（迁移有成本） | 降本；但餐饮全案强依赖 PS/AI 工作流，**不建议全面替换** |
| **C 外挂** | 修图 / 生图 / 抠图 / 放大交给本地开源 AI 工具链 | 高 | 氛围图 / KV / 材质图自建产线，天然满足「零水印 · 零 Logo · 零文字」 |

**一句话总结：主人不需要「换掉 Adobe」，而是给 Adobe 装上「开源自动化 + 本地 AI」两条外挂 —— Logo/VI 继续矢量精绘，氛围图/修图走本地开源链。**

---

## 二、四层生态地图

```
┌─ A 加装层：Adobe 本体自动化 ────────────────────────────────┐
│   脚本(JSX) · 插件(UXP/CEP) · 库(Python/C++/TS)              │
│   代表：photoshop-python-api · illustrator-scripts 集合      │
├─ A2 AI 驱动层：让 LLM 直接开 Adobe ────────────────────────┤
│   官方 MCP「Adobe for creativity」· 社区 MCP · sd-ppp 插件    │
├─ B 替换层：开源平替 ───────────────────────────────────────┤
│   GIMP · Inkscape · Krita · Penpot · Darktable · Kdenlive…   │
├─ C 外挂层：本地 AI 图像工具链 ─────────────────────────────┤
│   ComfyUI · InvokeAI · rembg · IOPaint · Upscayl             │
└─ D 技能层：Agent Skills 生态（可对接蜂群）──────────────────┘
    anthropics/skills · superpowers · awesome-claude-skills …
```

---

## 三、逐类精选清单

### 3.1 A-1｜Adobe 本体的开源自动化（脚本 / 插件 / 库）

| 项目 | ★ | 许可 | 语言 | 用途 | 落地建议 |
|---|---|---|---|---|---|
| loonghao/photoshop-python-api | ~780 | MIT | Python | 用 Python(COM) 全量控制 PS：新建文档/图层/文字/批量导出 | ⭐ **最高性价比**，可直接进蜂群流水线 |
| loonghao/photoshop-python-api-mcp-server | ~255 | MIT | Python | 把上一行包装成 MCP，让 LLM 直接驱 PS | ⚠ 含「执行任意脚本」能力，须人工审批 |
| alisaitteke/photoshop-mcp | ~388 | — | TS | 另一套 PS MCP，自带本地 Web UI | 同上，安全面注意 |
| alexander-ladygin/illustrator-scripts | ~1.5k | — | JSX | 最火的 Illustrator 脚本集 | 批量对齐 / 尺寸 / 导出 |
| creold/photoshop-scripts | ~123 | MIT | JSX | CSV 生成画板、批量改文字、导出预览、按色选形 | 规格表 / 名片批量生成可用 |
| nvkelso/illustrator-scripts | ~270 | — | JSX | 制图向 AI 脚本（字体/图形替换、信息图） | 版式批处理 |
| AdobeDocs/uxp-photoshop-plugin-samples | ~357 | Apache-2.0 | JS | Adobe **官方** UXP 插件样例 | 自研插件的起点 |
| Adobe-CEP/CEP-Resources | ~1.84k | Apache-2.0 | JS | 官方 CEP 扩展工具与文档 | 老插件维护 |
| Adobe-CEP/Getting-Started-guides | ~641 | Apache-2.0 | JS | CEP 入门样例 | 同上 |
| docsforadobe/Types-for-Adobe | ~644 | — | TS | 全 Adobe 套件脚本 API 类型定义 | 写插件必装 |
| EmilDohne/PhotoshopAPI | ~373 | — | C++/Py | 直接读写 PSD/PSB 的解析库 | PSD 批处理 / 校验 |
| antipalindrome/Photoshop-Export-Layers-to-Files-Fast | ~1.6k | — | JSX | 图层导出成文件，比内置快得多 | 交付切图 |
| inlife/nexrender | ~1.85k | — | JS | After Effects 数据驱动渲染自动化 | 若做动态 KV |
| lfr7610/AiCommandPalette | — | MIT | JS | Illustrator 命令面板 + 工作流编排 | 提效小工具 |

### 3.2 A-2｜AI 直接驱动 Adobe（2026 的关键新变量）

| 项目 / 服务 | 类型 | 许可 | 说明 |
|---|---|---|---|
| **Adobe for creativity MCP** | **官方远程 MCP** | 商业服务 | 端点 `adobe-creativity.adobe.io/mcp`，**2026-04 GA**，50+ 工具覆盖 PS/AI/Firefly/Express/Pr/Lr/ID/Stock；游客约 40 工具，登录后更多。**只在聊天会话内工作，不会自动跑** |
| Adobe for ChatGPT | 官方 | 商业服务 | 2025-12 上线，ChatGPT 内 PS / Express / Acrobat 编辑 |
| Adobe Express Developer MCP | 官方（本地 npx） | 商业服务 | 开发 Express 插件用，**不改内容** |
| mikechambers/adb-mcp | 社区 | — | 通过本地 UXP 插件驱动**桌面版** PS/Pr 全功能 |
| matrayu/adobe-mcp | 社区 | — | 同上，驱动已安装的桌面应用 |
| zombieyang/sd-ppp | 社区 UXP 插件 | GPL-3.0 | 把 ComfyUI / Flux / Midjourney / replicate / RunningHub 接进 PS；2.0 需 PS2025+ |

> **关键判断**：官方 MCP 走的是 **Express / Firefly 级别**，不是桌面 PS/AI 全功能；要「脚本级」控制桌面版，仍得走社区 MCP 或 Python 库。**这是最容易被标题误导的一点。**

### 3.3 B｜开源替代品（逃离订阅）

| Adobe 产品 | 首选开源替代 | ★ | 许可 | 评价 |
|---|---|---|---|---|
| Photoshop | **GIMP** | — | GPL-3.0 | 老牌；UI 陈旧；PSD 兼容有坑 |
| Photoshop（绘画向） | **Krita** | 10.5k | GPL-3.0 | 绘画 / 插画首选，非修图 |
| Illustrator | **Inkscape** | — | GPL-3.0 | SVG 原生，矢量排版强；脚本发现性弱 |
| InDesign | Scribus | — | GPL-2.0 | 排版可行，生态小 |
| Lightroom | Darktable | — | GPL-3.0 | RAW 非破坏式 |
| XD / Figma | **Penpot** | ~60k | MPL-2.0 | 设计与代码协作，可自托管，自带 MCP |
| Premiere | Kdenlive | — | GPL-3.0 | 时间线剪辑 |
| After Effects | Natron / Blender | — | GPL-2.0 | 合成 / 特效 |
| Audition | Audacity | — | GPL-2.0 | 音频 |
| Acrobat | Stirling-PDF / PDF Arranger | — | MIT / GPL | PDF 合并拆分 |
| 像素画/2D | PixiEditor | 8k | LGPL-3.0 | 像素 + 矢量 + 动画 |
| **汇总索引** | **KenneyNL/Adobe-Alternatives** | 8.7k | — | 覆盖 16 个 Adobe 产品的最佳平替清单（2026-06 更新） |

### 3.4 C｜本地 AI 图像工具链（生图 / 修图 / 抠图 / 放大）

| 工具 | ★ | 许可 | 用途 | 商用注意 |
|---|---|---|---|---|
| **ComfyUI** | 136k | GPL-3.0 | 节点式生图引擎，支持 FLUX / SD3.5 / Qwen-Image | 自用 / 内部 OK；做在线服务须开源 |
| AUTOMATIC1111 WebUI | 164k | AGPL-3.0 | 经典 SD WebUI，扩展最多 | AGPL，云端服务会咬人 |
| Fooocus | 51k | GPL-3.0 | Midjourney 式极简，零配置 | — |
| **InvokeAI** | 28k | **Apache-2.0** | 专业画布，内绘/外绘/迭代 | **商用最友好，推荐团队用** |
| Upscayl | 49k | AGPL-3.0 | AI 放大（Real-ESRGAN），有桌面版 | 内部 OK；在线卖须开源 |
| **rembg** | 25k | **MIT** | 一键抠图，支持批量 / HTTP / FFmpeg | **最宽松，协议最稳** |
| **IOPaint** | 21.7k | **Apache-2.0** | 去水印 / 去路人 / 外扩画幅 / 换物体 | 开源版「内容识别填充」 |
| RMBG-2.0 (briaai) | — | 模型权重另有条款 | 抠图精度标杆 | 商用须看模型卡许可 |
| GFPGAN / Real-ESRGAN | — | BSD / 自定义 | 人脸修复 / 超分 | 看具体许可 |
| Upscayl 同类：QualityScaler | 3.2k | MIT | 本地放大/去噪 | MIT |

> **对主人的价值**：氛围图 / KV / 插画 → ComfyUI（本地）；菜品图 / 商品图批量抠图 → rembg（MIT，最稳）；素材去水印 / 补边 → IOPaint；糊图放大 → Upscayl。**全部本地，天然不加水印、不落别人服务器，符合「生图三零」铁律。**

### 3.5 D｜Agent Skills 生态（可对接蜂群）

| 项目 | ★ | 说明 |
|---|---|---|
| anthropics/skills | 官方 | SKILL.md 格式标准参考；多技能 Apache-2.0（docx/pdf/pptx/xlsx 为 source-available） |
| obra/superpowers | ~40.9k | 最流行的技能方法论：需求→规格→计划→子代理→TDD→评审 |
| ComposioHQ/awesome-claude-skills | ~76k | 最大技能目录之一 |
| VoltAgent/awesome-agent-skills | — | 人工筛选，质量优先（1000+ skills） |
| vercel-labs/agent-skills | ~22k | Web 设计规范审查 |
| ui-ux-pro-max-skill | — | 设计智能系统（样式/配色/字体库检索） |
| anthropics/skills → brand-guidelines | 官方 | 品牌规范技能，**与主人 VI 业务直接同构** |

> **信号**：Skills 正在从「Claude 专属」演化为**跨 Agent 通用能力模块**（Codex / Cursor / Gemini CLI 都读 SKILL.md）。这与主人蜂群「角色卡 + Git」的打法**同构** —— 蜂群可直接吸收这套开放标准。

---

## 四、许可证合规矩阵

| 许可 | 能否商用 | 能否闭源分发 | 云端服务风险 | 代表项目 |
|---|---|---|---|---|
| **MIT** | ✅ | ✅ | 无 | rembg · photoshop-python-api |
| **Apache-2.0** | ✅ | ✅ | 无（含专利授权） | InvokeAI · IOPaint |
| **MPL-2.0** | ✅ | 修改过的文件须开源 | 低 | Penpot |
| **GPL-3.0** | ✅ | ❌ 分发须开源 | 仅分发时触发 | ComfyUI · Krita · sd-ppp |
| **AGPL-3.0** | ✅ | ❌ | **高：通过网络提供服务也须开源** | Upscayl · A1111 |

> **红线**：把 Upscayl / ComfyUI / A1111 做成**对外在线服务收费** → AGPL/GPL 传染条款即触发。
> **安全区**：自用、内部团队用、把成品交付给客户 —— **均不触发**。

---

## 五、与主人现有产线的结合点

| 主人环节 | 推荐方案 | 理由 |
|---|---|---|
| Logo / VI 矢量精绘 | 保持手写 SVG；Inkscape 做辅助校对与批量导出 | 铁律：标识禁生图 |
| 规格表 / 名片 / 批量文案 | creold 脚本集 + photoshop-python-api | CSV→画板、多文字批改 |
| 交付切图 | Photoshop-Export-Layers-to-Files-Fast | 图层批量导出，快 |
| 氛围图 / KV / 插画 | ComfyUI（本地 FLUX / SD3.5） | 满足「三零」 |
| 菜品图 / 商品图抠图 | rembg（MIT） | 批量、离线、协议最稳 |
| 素材去水印 / 补边 | IOPaint（Apache-2.0） | 开源版内容识别填充 |
| 糊图 / 小图放大 | Upscayl 桌面版 | 双击即用 |
| 「让 AI 直接改 PS」 | photoshop-python-api-mcp-server | 走蜂群 agent 调用 |
| 网页 / 移动设计协作 | Penpot（自托管 + MCP） | 降本 + 文件自主 |

---

## 六、落地优先级

**P0 — 立刻可上，零风险**
1. **rembg**（MIT）→ 抠图批处理脚本，接入蜂群
2. **creold/photoshop-scripts** + antipalindrome 导出脚本 → PS 内装即用
3. **Upscayl** 桌面版 → 图片放大

**P1 — 需小配置**
4. **loonghao/photoshop-python-api**（MIT）→ 写「批量导出 / 批量改文字」自动化
5. **IOPaint** → 去水印 / 外扩
6. **Inkscape / GIMP** → 作为 Adobe 的备份与免费场景

**P2 — 需评估**
7. **photoshop-python-api-mcp-server** → 让蜂群直驱 PS（配人工审批）
8. **ComfyUI** 本地部署 → 氛围图产线
9. **Penpot** 自托管 → 团队协作与设计系统

---

## 七、风险与取舍

1. **安全面**：MCP 类项目内置「执行任意脚本 / 代码」能力（第三方审计对 photoshop-python-api-mcp-server 给出 1 项 Critical 级告警）。**必须走人工审批，禁止无人值守。**
2. **活跃度不均**：IOPaint 最后提交约 2025-04；Upscayl 发行版停在 2024-12（代码仍在更）。**选项目优先看「最近提交」，而非 star。**
3. **PSD 兼容陷阱**：GIMP/Krita 打开含矢量图层或高级特性的 PSD 会丢内容 —— 替代品**不能**做「往返编辑」主力。
4. **替代品学习成本**：Inkscape/GIMP 的 UI 与 AI/PS 差异大，餐饮全案交付节奏紧，**全面替换不划算**。
5. **官方 MCP 边界**：Adobe 官方 MCP 只到 Express/Firefly 级别，替代不了桌面全功能。
6. **数据口径**：本文 star 为第三方快照，与 GitHub 实时可能存在 ±5% 偏差；许可未确证处已标 `—`。

---

## 八、一句话总纲

> **「不换工具，加装能力」** —— Adobe 本体用开源脚本 / MCP 提效，图与素材交给本地开源 AI 工具链；Logo 继续手绘矢量，其余尽量离线自产。
