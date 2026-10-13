# brand-system-skill 全面分析报告

> 分析人：蜂王（W1 采集 + W4 审查 + 蜂王聚合） · 档位：STRICT（主人点名深挖） · 日期：2026-10-06
> 被审对象：`amirmushichge/brand-system-skill` v0.2.0-alpha

## 零、一句话结论

**这是一份"把品牌设计总监的工作方法写成协议"的文档，而不是一个工具。**
它的价值 90% 在**流程纪律**，10% 在生成能力 —— 而这个"流程纪律"，恰好就是主人蜂群体系一直在手工维护的东西。**建议：吸收其协议骨架，不引入其执行依赖。**

---

## 一、身份证

| 项 | 值 |
|---|---|
| 仓库 | `amirmushichge/brand-system-skill` |
| Skill 名 | **`brand-system-builder`** |
| 版本 | **v0.2.0-alpha**（2026-08-11 发布） |
| 作者 | Amir Mushich（个人，[@AmirMushich](https://x.com/AmirMushich)），X 上活跃 |
| 许可 | **CC-BY-4.0** —— 允许商用，**但要求署名** |
| 形态 | **纯 Markdown**：1 个 SKILL.md + BENCHMARK.md + CHANGELOG + CITATION + CONTRIBUTING + assets/ |
| 依赖 | **零脚本、零代码、零网络请求**（攻击面 ≈ 0） |
| 优化目标 | `optimized_for: Lovart Agent Thinking Mode` |
| 数据 | ★134 · fork 13 · issue 2 · 与 `lovartai/lovart-skill` **无关**（独立社区项目） |

> 关键区分：**它不是 Lovart 官方 skill**。官方那个是 `lovartai/lovart-skill`（可执行、需付费）。这个 **是纯文档**，最佳体验需在 Lovart Agent 里跑。

---

## 二、核心哲学（这是它最值钱的部分）

> **"Extract the logic of a reference. Do not copy its identity."**
> （提取参考的逻辑，不要抄袭它的身份。）

以及 README 里那句：

> **"Prompts produce outputs. A Skill gives the Agent a process."**
> （提示词产出结果，Skill 给 Agent 一套流程。）

**这两句直接击中主人蜂群的立身之本** —— 蜂群的价值从来不是"能生图"，而是"有流程"。

---

## 三、协议骨架解剖

### 3.1 二十条 Operating Rules（实际是"防呆清单"）

摘其精华：

| # | 规则 | 对应主人的已有铁律 |
|---|---|---|
| 2 | **Ask for missing information instead of inventing it** | ✅ 样张零编造 |
| 3/4 | **Never generate assets before the relevant approval gate** | ✅ 不可逆动作先问 |
| 8 | **在使用多个参考时，给每个参考指定一个明确角色** | ⭐ 蜂群尚无此条 |
| 9 | **Never let an external scene reference override the approved brand identity** | ⭐ 蜂群尚无此条 |
| 10 | 用 Agent 生成完整广告资产，**不要把"精修工具"当作规模化手段** | 新 |
| 12 | **不得声称概念包装图是生产就绪文件** | ✅ 能力边界诚实 |
| 16 | **每次耗积分生成前必须提交 Generation Plan 并等待批准** | ✅ 不可逆先问 |
| 18 | **只用真实存在的 Google Fonts，并在首次生成前点名到字族** | ✅ 字体必须可商用 |
| 19 | **绝不用"新旧方向混合"来拯救一个被否决的方向** | ⭐⭐ **这条极关键** |

**规则 19 值得单独拎出来**：主人的踩坑库里反复出现"在旧版上改"导致的污染问题（`overflow:hidden` 静默裁剪、批量替换吃掉包裹层、把已验证实现"顺便升级"）。**这与规则 19 是同一个病理**：**不要在污染源上做增量修补。**

### 3.2 Never Invent 清单（12 项禁止编造）

产品宣称 / 成分 / 认证 / 包装尺寸 / 法规文案 / 受众调研 / 市场数据 / 已批颜色 / 已批字体 / SKU 名 / 制造规格 / 品牌历史。

> 与主人的「**样张零编造**」完全同源，且**把边界列得更细**。可直接抄进蜂群制度。

### 3.3 Project State（项目检查点，14 字段）

```
PROJECT NAME / CURRENT STAGE / BRIEF STATUS / REFERENCE STATUS /
ANCHOR STATUS / BRAND LOCK STATUS / APPROVED DECISIONS / ACTIVE REFERENCES /
REFERENCE ROLES / LOCKED BRAND RULES / PROHIBITED STYLES / OPEN ISSUES /
GENERATED DELIVERABLES / NEXT ACTION
```

> **这就是一个状态机。** 每个阶段结束更新一次 —— 比"多轮自由对话"可控得多。蜂群目前靠"任务图 + 验收单"手工维护同类信息。

### 3.4 Workflow Map（完整 15 环）

```
ONBOARDING
→ PROJECT BRIEF              ← GATE 1
→ REFERENCE DECONSTRUCTION   ← GATE 2
→ FIRST BRAND KIT
→ CREATIVE-DIRECTION REVIEW  ← GATE 3
→ ANCHOR APPROVAL
→ BRAND GUIDELINES
→ KEY VISUAL SYSTEM
→ BRAND LOCK SETUP           ← GATE 4
→ CAMPAIGN ASSET GENERATION
→ CONSISTENCY AUDIT
→ CORRECTION LOOP
→ PACKAGING CONCEPTS
→ FINAL SYSTEM REVIEW
→ OPTIONAL EXTENSIONS (A/B/C/D)
```

**四道 APPROVAL GATE**：项目简报 / 参考方向 / Anchor Brand Kit / Brand Lock。
**铁律**：Anchor Brand Kit **未获批准前，不得生成任何 guideline / campaign / packaging**。

---

## 四、四大核心机制（逐条拆解）

### 机制 1 · Generation Plan（生成计划门）

**每一次**耗资源的生成前，必须先提交这份计划并等批准：

```text
GENERATION PLAN
Objective:                     目标
Deliverable:                   交付物
Inputs:                        输入
References and their roles:    参考 + 各自的角色
Locked decisions:              已锁定决策
Elements that may change:      允许变动的元素
Exact Google Fonts to use:     精确到字族
Prohibited elements:           禁止元素
Number and format of outputs:  产出数量与格式
```

> **评价**：这是**"先出 spec 再执行"的强制化**。与主人"先列执行清单再动手"的习惯完全同频，但它把这个习惯**写成了不可跳过的关卡**。
> **对蜂群的启发**：可给工蜂派工单**增设一个「生成计划」字段**，专用于产出类任务。

### 机制 2 · Brand Lock 三权分立 ★ 最有价值的机制

**问题的本质**：用 AI 生成新场景时，最大的风险是"参考图把品牌身份吃掉了"。

**解法**：把控制权**按维度切分给三个不同来源**，谁也不许越界。

| 控制方 | 被授权控制 | 被禁止控制 |
|---|---|---|
| **场景参考** | 构图族（非精确摆位）· 镜头类型 · 机位距离族 · 光照方向与质感 · 材质类别 · 景深与留白行为 · 视觉节奏 · 情绪张力 | ❌ 品牌身份 |
| **品牌锚点 (Anchor Kit)** | Logo · 字体 · 颜色 · 层级 · 图形语言 · 留白行为 | — |
| **包装/产品参考** | 产品形态 · 产品设计 · SKU 架构 · 标签分区 · 已批产品细节 | — |

**且明确规定"生成场景必须实质性改变"**：人物身份 / 姿势手势 / 服装造型 / 环境地点 / 道具摆位 / 背景建筑 / 产品互动 / 裁切与焦点关系 / 叙事细节 / 品牌专属色彩处理。

**明令禁止**：一对一副刻 · 近似重复场景 · 精确角色或姿势 · 精确物件排布 · **抄参考品牌** · **给别人的作品改个牌子**。

> **对蜂群的启发**：主人已有 **BrandLock 事实源**（土蚝小院做过 v1/v2），但那个 BrandLock 管的是"**品牌自身的常量**"；而这个 Brand Lock 管的是"**参考素材与品牌身份的权限边界**"。**两者是不同维度的东西，可以叠加。**
> 尤其是：主人做餐饮全案时经常需要"参考某家店的空间/氛围"，**Permission 边界一旦不清，产出的 KV 就会变成"给那家店改个牌子"** —— 这是真实的商业风险。

### 机制 3 · Consistency Audit（一致性审计）

审计维度 10 项：logo 准确性 / 字体族与字重字距 / 已批色与 SKU 逻辑 / 图形装置准确性 / 包装或产品形态 / 产品细节与标签分区 / 宣称准确性 / 构图角色合规性 / 禁止风格 / **外部场景参考的污染**。

输出结构：
```text
1. PASS      — 符合系统的元素
2. FAIL      — 脱离品牌的元素
3. SEVERITY  — critical / major / minor
4. CORRECTION— 精确要求的修改
5. PRESERVE  — 修正时必须保留的成功元素
→ 结论恒为三者之一：APPROVED / CORRECTION REQUIRED / REJECT AND REGENERATE
```

> **⛔ 与守卫蜂高度重合**！主人的守卫蜂验收单六项（完整性/准确性/格式/合规/可用性/一致性）里已经有"一致性"一项。
> **本 skill 的贡献是**：① **SEVERITY 三级**（守卫蜂目前是高/中/低，可对齐为 critical/major/minor）；② **PRESERVE 字段** —— **修东西时明确"什么不许动"**，这是守卫蜂目前缺的，而主人踩坑库里"修 A 坏 B"的案例不止一次。
> ③ **结论恒为三选一，不许骑墙** —— 守卫蜂已有"结论明确不骑墙"，此处可强化为**枚举式结论**。

### 机制 4 · REFINE vs REJECT AND RESTART（改 vs 推倒）

**这是整份文档最锋利的一刀。**

**REFINE（局部修正）** —— 仅当核心方向仍被认可、问题局部化：间距 / 一个色值 / 一种材质 / 一个 mockup / 一处文字层级 / 一个错误细节。

**REJECT AND RESTART（推倒重来）** —— 当反馈触及**多个基础系统**中任意组合：整体调性 · 字体系统 · 主色逻辑 · 材质语言 · 包装架构 · 视觉层级 · 摄影方向 · 目标客群适配 · 感知价格档次。

**外加四条触发**：① 第二次修正又引入新不一致；② 板面同时含新旧矛盾字体；③ Agent 无法可靠保持已批字体；④ 用户说"感觉根本不对"但指不出具体问题。

**重启时的五步纪律**：
1. 标记旧板面为 `REJECTED — DO NOT USE AS A VISUAL REFERENCE`
2. **只保留 KEEP 列表里的抽象决策**
3. **不得把被否决的板面作为生成参考附上**
4. 从零构建新概念
5. 生成前先出计划

> 🔥 **规则 19 复述**：**"Never blend a rejected direction with a replacement direction."**
> 混合的后果它写得很清楚：**混合字体、残留材质、矛盾颜色、视觉伪影**。

**这条与主人蜂群的踩坑库是同一个病根**：
- 2026-09-27：把**已验证正确的 px 上限**"改良"成百分比 → 22 张图被裁
- 批量替换时把 `.art-box` 包裹层连带吃掉 → 图片裸挂

**共同病理：在"已经不干净"的基础上叠加新决策。** 这份 skill 给出的解法是 —— **标记污染源、只保留抽象决策、物理隔离、从零重建**。**建议直接补进蜂群铁律。**

### 5 · 附加机制（值得一提）

| 机制 | 说明 | 评价 |
|---|---|---|
| **Creative Director Support Mode** | 当用户说"我不喜欢但说不出为什么"时，**停生成**，输出 `WHAT IS WORKING / WHAT MAY FEEL WRONG / WHY / KEEP-REMOVE-REFINE / 建议 / 2-3 个方向选项 + 权衡` | **极其实用** —— 专治"客户说不清需求" |
| **Mass-User-Friendly Briefing** | 每组最多问 3 个问题，不许一次性甩长问卷；术语必须用大白话解释 + 举短例 | 主人常对接非设计背景客户，**可直接复用** |
| **`HELP ME WITH THIS`** | 用户答不上来时，给 2-3 个明白选项 + 简短权衡 + 请其选择 | 回复即触发，降门槛 |
| **8 条 Recovery Commands** | `STATUS` / `RESUME` / `GO BACK` / `AUDIT` / `ART DIRECTOR REVIEW` / `REJECT DIRECTION` / `HELP ME WITH THIS` / `STOP` | **状态机式控制**，比自然语言可控 |
| **一模块一页（guideline）** | 「**每页只放一个 guideline 模块，绝不把多个模块塞进一页，也绝不压缩成 1-2 页密排总览**」 | ⭐⭐⭐ **与主人"一物料一页"铁律完全一致** |

> **注意最后一条**：原文写得斩钉截铁 ——
> *"Generate exactly one slide per guideline module. Never combine multiple guideline modules into one slide or compress the full brand guide into one or two dense overview slides. Prioritize legibility and image quality over compactness."*
> 主人 2026-09-22 定的「一物料一页」，**在这里得到了跨项目的独立印证**。这不是巧合 —— 是同一个道理的两次发现。

---

## 五、35 分评分量表（BENCHMARK.md）

| # | 维度 | 分值 |
|---|---|---|
| 1 | Workflow Compliance 流程合规 | /5 |
| 2 | User Guidance 用户引导 | /5 |
| 3 | Reference Independence 参考独立性 | /5 |
| 4 | Anchor Brand Kit Quality 锚点质量 | /5 |
| 5 | Brand Adherence 品牌依从性 | /5 |
| 6 | **Brand Lock Performance** 三权分立表现 | /5 |
| 7 | Correction Quality 修正质量 | /5 |
| | **合计** | **/35** |

**评级**：31–35 可发布级 · 25–30 良好 · 18–24 需再迭代 · <18 需大改。

**附带的测试报告模板**（可直接复用）：

```text
TEST ID / SKILL VERSION / DATE / MODE / LOADING METHOD /
CATEGORY / NUMBER OF SKUs / REFERENCE TYPE

SCORES: 七项 /5 → TOTAL /35

WHAT WORKED / WHAT FAILED / UNEXPECTED BEHAVIOR /
MANUAL INTERVENTIONS / HALLUCINATIONS / SKIPPED GATES / PROPOSED CHANGES
```

> **评价**：**"SKIPPED GATES"（跳过了哪些关卡）单列** —— 这是把"流程纪律"本身当成可审计对象。**蜂群可以借鉴：验收单增加「本轮跳过了哪些关卡」字段。**

---

## 六、与蜂群体系的对照总表

| 维度 | brand-system-skill | 蜂群现状 | 差距 |
|---|---|---|---|
| 流程承载 | 20 条规则 + 15 环工作流 | 蜂王六步 + 铁律 10 条 | **互补**，各有胜场 |
| 状态管理 | 14 字段 Project State | 任务图 + 验收单 | 蜂群较手工 |
| 关卡 | 4 道 Approval Gate + 强制 Generation Plan | G1/G2/G3 + 不可逆先问 | **同构**，可互相校准 |
| 参考素材管理 | **Brand Lock 三权分立** | ❌ 无 | **蜂群缺口** |
| 否决处理 | **REFINE vs REJECT AND RESTART** | ❌ 无明确判据 | **蜂群缺口** |
| 验收 | Consistency Audit + 三级严重度 + PRESERVE | G3 六项 + 高中低 | **蜂群缺 PRESERVE** |
| 评分 | 35 分量表 | 无量化 | 蜂群较定性 |
| 客户沟通 | Creative Director Support Mode + HELP ME WITH THIS | 依赖蜂王个人判断 | **蜂群可补** |
| 专业审查 | 全维 | 守卫蜂更强（含源码审计、合规、机检） | **蜂群更强** |

**结论**：**蜂群在"技术验收"上更强**（机检、探针、源码审计）；**本 skill 在"创意流程与客户协作协议"上更细**。**取长补短，不替换。**

---

## 七、风险与边界（诚实标注）

| # | 风险 | 严重度 | 说明 |
|---|---|---|---|
| 1 | **执行依赖强绑定 Lovart** | 中 | 最佳体验需 Lovart Agent + Thinking Mode；Lovart **不接受 .md 附件**，只能复制粘贴 SKILL.md 全文 |
| 2 | **alpha 阶段** | 中 | v0.2.0-alpha，协议可能变动；作者为个人，单点维护 |
| 3 | **CC-BY-4.0 署名义务** | 中 | 内部借鉴方法论不涉分发风险低；**对外发布衍生作品须署名 Amir Mushich** |
| 4 | **生成模型会扭曲文字** | 低 | 作者自陈：字体与文案须人工核 —— **未越界承诺** |
| 5 | **概念稿 ≠ 生产文件** | 低 | 明确声明包装图不是刀模/矢量/印前/量产规范 |
| 6 | **国内可访问性** | 待验 | lovart.ai 在内地的访问情况未实测 |

> **正面**：**它没有一句过度承诺**。对能力边界的诚实度，高于多数开源 skill。

---

## 八、给主人的吸收建议（具体到可执行）

| # | 建议 | 落到哪 |
|---|---|---|
| 1 | **补一条铁律**：否决一个方向后，**禁止在其上做增量修补**；须标记污染源 + 只保留抽象决策 + 从零重建 | `蜂群制度总纲.md` |
| 2 | **Brand Lock 增设「三权分立」层**：参考素材 / 品牌锚点 / 产品包装 各管一摊，禁越界 | `BrandLock` 模板 |
| 3 | **验收单增设 `PRESERVE` 字段**：修正时明确"什么不许动" | `验收清单.md` G3 |
| 4 | **严重度对齐**：高/中/低 → critical / major / minor（可选） | `验收清单.md` |
| 5 | **验收单增设「本轮跳过的关卡」字段** | `02-验收单.md` 模板 |
| 6 | **派工单增设「生成计划」字段**（产出类任务必填） | `派工单模板.md` |
| 7 | **`Never Invent` 12 项清单抄进制度** | `蜂群制度总纲.md` |

---

## 九、本次未覆盖（必填边界）

1. **未实测运行** —— 未注册 Lovart、未在 Lovart Agent 内实跑一次完整 12 阶段。
2. **未做跨版本对比** —— 仅读到 v0.2.0-alpha 与 v0.1.0-alpha 的 changelog 差异，未看 commit 级演进。
3. **`assets/` 目录内容未展开**（从文件树看为图片资源）。
4. **非官方项目** —— 与 Lovart 官方无隶属关系，平台方是否长期兼容未知。
