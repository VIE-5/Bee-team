# lovart 相关 Skills 资料包

> 侦查时间：2026-10-06 · 工单：T1 · 样本量：14 条（精确命中 0）
> 侦查员：W1 资料侦查蜂

## 零、关键词校正（最重要的一条）

| 检索词 | GitHub 仓库命中 | 结论 |
|---|---|---|
| **lovrat**（主人原词） | **0 条** —— GitHub 仓库搜索直接返回「Your search did not match any repositories」 | **精确命中为零** |
| **lovart**（一字之差） | 有效命中 ≥14 条仓库 | **真实目标词** |

> 判定依据：`https://github.com/search?q=lovrat&type=repositories` → 「Your search did not match any repositories」（2026-10-06 实测）。
> 结论：主人所指的应是 **Lovart**（AI 设计/多模态生成平台），"lovrat" 系 `a`→`r` 的字母换位（typo）。
> **Lovart 是一家 AI 设计 Agent 产品**（官网 lovart.ai），围绕它形成了一批开源 skill / 复刻项目。

---

## 一、核心结论（5 条，每条带来源）

1. **「lovart」官方 skill 只有一个：`lovartai/lovart-skill`（★134）** —— 由 Lovart 官方组织账号发布，MIT 许可，Python 零依赖，是**调用 Lovart Agent OpenAPI 生成图像/视频/音频/3D 的薄客户端**。
   来源：[github.com/lovartai/lovart-skill](https://github.com/lovartai/lovart-skill)

2. **存在一个「Lovart 替代品 / 开源复刻」赛道（非 skill，但同为 lovart 生态）** —— 如 `xiaoju111a/OpenLovart`(★291)、`fancyboi999/Loomic`(★273)、`Anil-matcha/Open-AI-Design-Agent`(★389)、`hsaigroup/open_tapnow_lovart`(★35)、`greatriver2046-hue/lingdraw-OpenLovart`(★34)。这些是**自建 AI 设计画布应用**，不是可插拔 skill。
   来源：[github.com/search?q=lovart](https://github.com/search?q=lovart&type=repositories)

3. **对主人业务最有价值的一条：`amirmushichge/brand-system-skill`（★134）** —— 「把一张视觉参考 → 演化为完整品牌系统」的**引导式品牌工作流 skill**，含 Anchor Brand Kit、Brand Lock、一致性审计、35 分评分量表。**与主人餐饮品牌全案业务直接同频**，且是 CC-BY-4.0 可商用。
   来源：[github.com/amirmushichge/brand-system-skill](https://github.com/amirmushichge/brand-system-skill)

4. **「lovart skill」关键字下还有一条长尾（多为个人低星复刻/搬运）** —— `dreasky/lovart-skill`(★1)、`mucoQ/lovart-skill`(★0，日文)、`qqgg1988qq-oss/lovart-general`(★0)、`vip589455/lovart-skill`(★0，选品用途)、`IMMM666/lovart-print-skill`(★0)、`muhammad-ahmed-ghani/nano-banana-skills`(★2，标注为 Lovart 本地替代)、`hanmin12190906-ui/xiaomin-ecommerce-main-image-skill-claude`(★0，电商主图)。
   来源：[github.com/search?q=lovart+skill](https://github.com/search?q=lovart+skill&type=repositories&s=stars&o=desc)

5. **生态判断**：Lovart 官方 skill 走 **OpenClaw / Hermes Agent** 两个 agent 生态（`npx skills add` / 手动复制到 `~/.hermes/skills/`），**不是 Anthropic Claude Skill 官方格式**，但声明兼容 Claude Code / Cursor（凡能调 Python 的助手均可）。
   来源：[README.md](https://github.com/lovartai/lovart-skill/blob/main/README.md)

---

## 二、明细清单

### A. 真正的 Skill（可插拔 agent skill）—— 6 条

| # | 仓库 | 定位 | ★ | 语言 | 许可 | 最近更新 | 可信度 |
|---|---|---|---|---|---|---|---|
| 1 | [lovartai/lovart-skill](https://github.com/lovartai/lovart-skill) | **官方**。Lovart OpenAPI 薄客户端，出图/视频/音频/3D/编辑 + 项目线程管理 | 134 | Python | MIT | 2026-09-30 | 高 |
| 2 | [amirmushichge/brand-system-skill](https://github.com/amirmushichge/brand-system-skill) | **品牌系统工作流**。参考图→Anchor Brand Kit→Brand Lock→一致性审计 | 134 | Markdown | CC-BY-4.0 | 2026-08-11 | 高 |
| 3 | [dreasky/lovart-skill](https://github.com/dreasky/lovart-skill) | Lovart skill 复刻/搬运 | 1 | Python | 未标注 | 2026-03-24 | 低 |
| 4 | [mucoQ/lovart-skill](https://github.com/mucoQ/lovart-skill) | 日文版 Lovart 画像·动画生成 skill，适配 Claude Code/OpenCode/Codex/Antigravity | 0 | Python | 未标注 | 2026-04-19 | 低 |
| 5 | [qqgg1988qq-oss/lovart-general](https://github.com/qqgg1988qq-oss/lovart-general) | Lovart 出图 skill（Claude Code / OpenClaw） | 0 | Python | 未标注 | 2026-05-22 | 低 |
| 6 | [muhammad-ahmed-ghani/nano-banana-skills](https://github.com/muhammad-ahmed-ghani/nano-banana-skills) | Nano Banana Pro/2 skill，**自称 Lovart 的本地替代**（Canva+Cursor） | 2 | — | 未标注 | 2026-03-26 | 低 |

### B. 同生态但非 Skill（开源复刻 / 应用）—— 6 条

| # | 仓库 | 定位 | ★ | 语言 | 最近更新 | 可信度 |
|---|---|---|---|---|---|---|
| 7 | [Anil-matcha/Open-AI-Design-Agent](https://github.com/Anil-matcha/Open-AI-Design-Agent) | 开源 AI 设计 Agent，对标 Lovart/Runway/Luma/Krea | 389 | JavaScript | 2026-10-02 | 高 |
| 8 | [xiaoju111a/OpenLovart](https://github.com/xiaoju111a/OpenLovart) | 开源 AI 设计平台，AI 对话 + 智能画布 | 291 | TypeScript | 2026-01-23 | 高 |
| 9 | [fancyboi999/Loomic](https://github.com/fancyboi999/Loomic) | 开源 AI 画布设计 agent，Lovart/Canva AI 替代 | 273 | TypeScript | 2026-10-01 | 高 |
| 10 | [Xiangyu-CAS/codex-canvas](https://github.com/Xiangyu-CAS/codex-canvas) | Codex 无限画布插件（标签含 lovart/skills） | 135 | JavaScript | 2026-10-01 | 中 |
| 11 | [hsaigroup/open_tapnow_lovart](https://github.com/hsaigroup/open_tapnow_lovart) | 开源版 TapNow & Lovart（主打数据安全） | 35 | — | 2025-12-25 | 中 |
| 12 | [greatriver2046-hue/lingdraw-OpenLovart](https://github.com/greatriver2046-hue/lingdraw-OpenLovart) | LingDraw - 开源无限画布设计 agent | 34 | Vue | 2026-05-20 | 中 |

### C. 其他命中（弱相关）—— 2 条

| # | 仓库 | 说明 | ★ | 最近更新 |
|---|---|---|---|---|
| 13 | [ddlmanus/lovarts-drama](https://github.com/ddlmanus/lovarts-drama) | AI 短剧生产工作台（名字含 lovarts） | 30 | 2026-05-26 |
| 14 | [onlinedear/lovartutu](https://github.com/onlinedear/lovartutu) | 无描述 | 10 | 2026-01-23 |

> 另：`sol1560/Lovart-Unlocker`（第三方解锁工具，非 skill，无 GitHub 直链命中，仅见于 Lovart 官网博客）—— **合规风险高，不建议接触**。

---

## 三、值得深挖的线索

1. **`amirmushichge/brand-system-skill` 的 Brand Lock 机制** —— 它把「场景参考 / 品牌锚点 / 包装参考」三者的控制权分离，禁止一对一副刻。**这套「参考图不得直接复刻」的约束逻辑，可反哺主人现有的 BrandLock 事实源体系**（概念同源，可借鉴其"分权控制"表达）。
2. **官方 skill 的 `--subjects` / `--prefer-models` / `failures` 命令** —— 支持按模型指定（midjourney / gpt-image / seedream / flux / nano-banana），对未来做「模型路由」有价值。
3. **`BENCHMARK.md` 的 35 分评分量表** —— 用于给品牌系统工作流打分（流程合规 / 参考独立性 / 品牌质量 / Brand Lock 表现 / 修正质量），是可复用的**验收量表**范式。
4. **官方 skill 的 Thinking Mode** —— `--mode thinking` 深度结构化推理，宣称"适合复杂品牌系统"。与主人「先出 spec 再执行」的工作流天然契合。

---

## 四、未解决 / 存疑（必填，不许藏）

- 【**关键词不确定**】「lovrat」精确零命中。本包按「lovart 拼写近似」采集。**若主人本意另有其人（某个具体开发者/仓库名），需主人确认**。
- 【未核实】各仓库的 ★ 数、更新时间在多次检索间存在波动（125 / 129 / 132 / 134），系抓取时点与缓存差异，已取最新值并标注日期。
- 【**许可存疑**】B 组（OpenLovart / Loomic / Open-AI-Design-Agent 等）**许可证信息多为空白或未标注**，开源不等于可商用——须逐个核实 LICENSE 文件。
- 【样本偏差】GitHub 网页搜索为**相关度排序的前 N 条**，非全量；低星仓库可能被截断。本包为「轮廓级」而非「穷举级」。
- 【未核实】`lovartai` 是否为 Lovart 官方实体账号 —— 账号名与产品一致、仓库结构规范，**倾向官方但未见平台侧确认**。
- 【第三方目录数据冲突】skillselion 报 ★125、claudeskills 报 ★129、reporank 报 ★133、GitHub 实时 ★134 —— 第三方目录存在同步滞后，**以 GitHub 实测为准**。
