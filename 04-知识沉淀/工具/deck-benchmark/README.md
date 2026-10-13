# deck-benchmark · 册子对标分析工具包

> 用途：把两份**已交付的 PDF 册子**（提案册 / 全案册 / VI 册）做**结构与布局对标**，产出可量化差异 + A/B 可视证据。
> 核心立场：**一切数字以磁盘实测为准，不引用任务图自述；不借道缩略图目视估。**
> 首用于 2026-09-27「碗香 × 土蚝小院 V6」，产出 `03-任务档案/20260927-碗香PDF封装排版/06-对标分析-土蚝V6.md`；
> 结构底稿见同目录 `09-V6结构与板块拆解.md`（源 + PDF 双向取证的完整拆解范例）。

---

## 环境

```bash
PY=C:/Users/27612/.workbuddy/binaries/python/envs/default/Scripts/python.exe
```

依赖 `pymupdf`（已装在上述 venv，版本 1.28.2）。

---

## 八个工具

| 脚本 | 作用 | 用法 |
|---|---|---|
| `probe_structure.py` | 页数 / MediaBox 尺寸集合 / 逐页页眉页脚 / 图像块 / 满幅出血 → 写 `<pdf>.probe.json` | `python probe_structure.py <pdf>` |
| `probe_geom.py` | 版心边距 / 页眉带 / 页脚带 / **完整字号集合** / 字体家族 | `python probe_geom.py <pdf> <页...>` |
| `probe_blocks.py` | **块级布局**：按 y 序输出该页所有文本块 + 图 bbox（还原单页骨架的关键） | `python probe_blocks.py <pdf> <页...>` |
| `probe_fit.py` | **图片贴合体检**：逐张图量「渲染尺寸 vs 容器」→ `CROP`/`DISTORT`/`COLLAPSE` | `python probe_fit.py <index.html>` |
| `probe_overflow.py` | **内容溢出体检**（不限于图）：递归量每页容器内所有元素 bottom vs 容器 bottom → `OVERFLOW`/`(偏空)` | `python probe_overflow.py <index.html> [容器选择器=.bd]` |
| `compare5.py` | 读两份 `.probe.json` 出五维汇总对比 | `python compare5.py A.pdf B.pdf A标签 B标签` |
| `make_ab.py` | A/B 并置对照图（左 A 右 B + ASCII 标签） | `python make_ab.py A.pdf B.pdf out.png A页 B页 "左标签" "右标签"` |
| `parse_source.py` | **源侧拆解**：从 `index.html` 出 页型家族 / 板块聚合 / 逐页标题层 / 页脚内容类型 / **结构自检**（板块缺章节页、物料页缺板块标记） | `python parse_source.py <index.html> [--out x.json]` |

> **`probe_fit.py` 与 `probe_overflow.py` 是一对「内容完整性机检双闸」** ——
> 前者查图片被裁（百分比 `max-height` 基准失效致原尺寸溢出），后者查**文本/栅格**被裁
> （多块两列自动行高撑爆容器）。两者都对应同一根因：`overflow:hidden` 静默裁掉超出内容，
> **而张数 / 体积 / md5 / PDF 页数这四项收尾指标在两种情况下全部正常**。
> 两个工具都需**双向验证**（正式产物 PASS + 已知坏样本 FAIL）后才算可用。

**顺序**：先 `probe_structure.py` 跑两份 PDF（生成 JSON）→ 再 `compare5.py`；若要拆「结构与板块」，另跑 `parse_source.py`（需要源 HTML）。
**交付前固定**：`probe_fit.py` + `probe_overflow.py` 都要跑，两者都须 PASS。

`parse_source.py` 适配新册子只改 `SELECTORS` 一张表；`PAGE_KINDS` 补充该册的结构性 class 即可。

---

## 五维对标清单（照做，不要漏维）

1. **几何** — 页数 / 画幅 / MediaBox / 文件体积 / 单页均重 / 版心左右 / 页眉带高 / 页脚带高 / 页码位置 / 满幅出血图层数
2. **页型家族** — **判据要分册取，别一刀切**：
   - **手写型 deck**（每页 markup 全量展开，如土蚝 V6 的 94KB `index.html`）→ **数结构性 class**（`.cover` / `.section` / `.bleed-*` / `.end` / 裸 `.slide`）
   - **函数型 deck**（页由生成器函数拼装，如碗香 `build.py`）→ **数生成器函数**（`r_plate` / `r_section` …）
   - 选**能得到「互斥页型集合」**的那一种，并交叉验证：**页型计数之和 == 总页数**
   - ⚠️ 别混用：碗香数 class 会被语义类淹没；**V6 数生成器则数不到 —— 它压根没有生成器**
   - 附加统计**单图页 / 多图页占比**（V6 单图版 41/60 = 68%，全册仅 1 页并置）
3. **贯通度** — 有页眉页数 / 有页脚页数 / 页眉承载的章节标记 / **正文零文本层页数**
4. **机制** — 亮度自适应、图版承托、生产标注是否清理、侧边页码等
5. **规范 token** — 栅格步长（是否按版心等分）/ 字号集合 / **字体：源侧看 `font-family` 栈，PDF 侧必须实测字体表**（见坑 4）

---

## 六条踩过的坑（读这段能省一轮）

### 坑 1 · 「正文零文本层」判据不能用字符数

第一版用 `n_txt_chars < 15` 判"裸图页"，结果碗香 0 页命中 —— 因为**页眉 + 页脚本身就有 60 字**。
**正确判据是 `n_blocks == 0`（正文块数）**。改后：碗香 42/55（76%），V6 0/60。

### 坑 2 · 字号档数别看「加权 Top N」

按字符数加权看前 12 档，会得出「V6 12 档 vs 碗香 6 档」的错觉。
**取完整集合后真相是 23 档 vs 19 档 —— 方向相反。**
→ 要报字号体系，必须打印**全量集合**，不要用 `.most_common(12)`。

### 坑 3 · 多张对照图体积相近 ≠ 内容相同

同一画布 + 相近熵值，3 张不同的 A/B 图体积可能只差 6 字节。
**验收必须看 md5**，不要用文件体积判断是否换了内容（与 `MEMORY.md` §「别信退出码」同源）。

### 坑 4 · 第⑤维「字体」只 grep 了源、没实测 PDF → 漏掉「全册 100% Type3」

首轮做第⑤维时，只在源 CSS 里 `grep font-family` 看了字体栈，**没读交付 PDF 的字体表** ——
于是漏掉了「碗香 60 页一个字体都没嵌入」这个真实发现（对照 V6 有 Georgia/Arial 真嵌入）。

**本维必须两侧都做**：

```python
# PDF 侧：统计非 Type3 字体
from collections import Counter
f = Counter(s["font"] for p in doc for b in p.get_text("dict")["blocks"]
            for l in b.get("lines", []) for s in l["spans"])
t3 = sum(v for k, v in f.items() if k.startswith("Type3"))
print("Type3 占比 %d/%d" % (t3, sum(f.values())), [k for k in f if not k.startswith("Type3")])
```

**判据**（已隔离实验验证）：**字体族命中「可变字体 VF」或「未安装字体（走系统回退）」→ Chrome 打印只能退化为 Type3；命中「已安装静态字体」→ 真实嵌入。**

- 本机 `NotoSerifSC-VF.ttf` / `NotoSansSC-VF.ttf` 是 **VF** → 用它们排中文的册子**中文层全 Type3**
- 静态可用的：`SimSun` / `Microsoft YaHei` / `SimHei` / `KaiTi` / `FangSong`（中文）、`Georgia` / `Arial` / `Times New Roman`（西文）
- **V6 的做法值得学**：`--font-en:` 指向 Georgia、`--font-num:` 指向 Arial（都落到静态）→ 西文与数字层真嵌入；中文层仍是 VF → Type3。**这解释了 V6 里那 4 个非 Type3 字体**
- 性质：Type3 **不是「看起来不对」，是交付工艺项**（部分印厂 preflight 会因「未嵌入字体」报警）→ 归入**质量差异**，须报但不必判为视觉缺陷

### 坑 5 · 同名不同本 —— **认画幅页数，不认文件名**

土蚝小院目录里有 5 份近名 PDF，只有 1 份是标杆正本：

| 页数 | 画幅 | 体积 | 判定 |
|---|---|---|---|
| **60** | **1020×637.92 pt (16:10)** | 90.7 MB | ✅ V6 正本 |
| 40 | 1440×810 (16:9) | 57.4 MB | ❌ 旧版（`品牌视觉资产封装/index.pdf`） |
| 25 / 29 | 1440×810 | 43.5 / 28.8 MB | ❌ 更早的版本 |

**动手前先出这张表**：`页数 / MediaBox / md5`。名字一样、体积接近，都可能是另一本。
（同名不同本曾导致「交付 PDF 是过期版本」被 G3 打回，见踩坑库 2026-09-27 专条。）

### 坑 6 · 源不在成品目录里 —— 先找源，再谈复用

`E:\唐V-work\土蚝小院\` 下**只有成品 PDF 与探针 JSON，没有 V6 的源**。
V6 的真源在任务档案：`03-任务档案\20260921-土蚝小院品牌全案封装\01-工蜂产出\index.html`（含 `<!-- P04 · 品牌速览 -->` 逐页注释，可**直接当结构清单用**）。

**做法**：拆结构前先 `grep -rl "<关键词>"` 定位源；`find / -iname "*v6*"` 这类按名搜常常落空。

---

## 输出纪律

- 逐项标注 **「需求差异 vs 质量差异」**：画幅比例 / 图占幅 / 页眉栏数 / 页码位置 / 并置 vs 拆页 属**需求差异**，判成缺陷即误判。
- 对标报告末尾必须有 **「修正的上轮结论」** 一节：本轮实测推翻了上轮哪条结论，写清楚。
- A/B 图产物核对：`md5` 各不相同 + **缩一版目视确认真换了内容**。
- 拆结构时**必跑 `parse_source.py` 的自检两问**：① 每一个板块的首个内容页，其前一页是不是章节页？② 有没有物料页缺任何板块标记？—— 标杆册自己也可能漏（V6 就漏了「伍」的章节页）。
- 板块归属**以页眉栏目（`.chap`）为准，不靠页码区间猜**；页型**以源 class 为准，不靠缩略图目视分**。
