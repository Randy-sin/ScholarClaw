# ScholarClaw 项目书

> 全自主学术研究引擎：从一句话到一篇可编译的会议论文

---

## 大纲

- **第一~二章**：背景与动机——是什么、为什么做
- **第三~四章**：技术核心——怎么做的
- **第五~六章**：质量与竞品——做得多好
- **第七~九章**：场景、技术栈与路线图——能用在哪、接下来做什么
- **第十章**：与 OpenClaw 的集成架构
- **第十一~十二章**：开源信息与总结愿景

---

## 一、项目概述

ScholarClaw 是一个**全自主的学术研究自动化系统**。用户只需输入一句自然语言描述的研究方向（例如"注意力机制在长序列时序预测中的效率优化"），系统即可自主完成从文献检索、假设生成、实验设计与执行、论文撰写到引用验证的全流程，最终输出一篇 5,000–6,500 词、可直接在 Overleaf 上编译的会议级论文（支持 NeurIPS、ICML、ICLR 模板）。

**核心数据：**

| 指标 | 数值 |
|------|------|
| 流水线阶段数 | 12 个阶段，5 个阶段组 |
| 测试用例数 | 1,117+ |
| 测试文件数 | 44 个 |
| 接入的学术 API | 5 个（arXiv、Semantic Scholar、OpenAlex、CrossRef、DataCite） |
| 支持的会议模板 | 6 套（NeurIPS 2024/2025、ICML 2025/2026、ICLR 2025/2026） |
| 实验执行模式 | 5 种（模拟、本地沙箱、Docker、SSH 远程、Google Colab） |
| 代码量 | Python 源码 60+ 模块，配置系统 200+ 参数 |

---

## 二、解决的核心问题

### 2.1 学术论文写作的痛点

撰写一篇合格的学术论文，研究者通常需要：

1. **文献检索**：在 Google Scholar、arXiv、Semantic Scholar 等多个平台反复搜索，筛选相关论文，手动整理 BibTeX——耗时数天到数周。
2. **实验设计与执行**：编写实验代码、调试环境、处理 GPU 兼容性、跑多组对比实验——耗时数周。
3. **论文撰写**：从大纲到初稿到修订，反复打磨引言、方法、实验、结论——耗时数周。
4. **引用管理**：确保每条引用真实存在、格式正确、与论文内容相关——极易出错。
5. **LaTeX 排版**：适配不同会议的模板要求（单栏/双栏、引用格式、页面布局）——繁琐且容易出格式问题。

这些步骤高度碎片化，每一步都需要不同的工具和专业知识，且步骤之间存在大量重复劳动。

### 2.2 现有工具的不足

| 现有方案 | 局限性 |
|---------|--------|
| ChatGPT / Claude 直接写论文 | 引用全部是幻觉（编造不存在的论文），无法运行实验，无法生成可编译 LaTeX |
| AI Scientist (Sakana AI) | 仅支持特定模板实验，不支持多源文献检索，无引用验证机制 |
| 手动使用多个工具组合 | 需要在 arXiv、Overleaf、Jupyter、Zotero 之间反复切换，效率低下 |

### 2.3 ScholarClaw 的解决方案

ScholarClaw 将上述所有步骤**串联为一条确定性流水线**，一次命令完成全流程：

```bash
scholarclaw run --topic "你的研究方向" --auto-approve
```

输出一个自包含的研究产物目录：

```
artifacts/sc-20260318-143022-a7f3/
├── deliverables/           ← 直接上传 Overleaf 编译
│   ├── paper.tex
│   ├── paper.pdf           ← 自动编译（需要 pdflatex）
│   ├── references.bib
│   ├── neurips_2025.sty
│   └── figures/
├── paper_draft.md          ← 5,000–6,500 词完整论文
├── experiments/            ← 可运行代码 + 结果
├── charts/                 ← 带误差线的对比图
├── peer_review.md          ← 自动评审报告
└── verification_report.json ← 引用审计记录
```

> **PDF 自动编译：** 如果运行环境安装了 `pdflatex`，流水线在交付阶段会自动将 `paper.tex` 编译为 `paper.pdf`，遇到常见 LaTeX 错误（缺包、未定义命令、浮动体溢出等）最多自动修复 3 次。如果未安装 `pdflatex`，流水线仍正常完成，输出 `.tex` + `.bib` 文件，用户可在 [Overleaf](https://overleaf.com) 上一键编译。

---

## 三、技术架构

### 3.1 流水线总览

系统采用**阶段化流水线架构**，12 个阶段按职责划分为 5 个阶段组：

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  Discovery（探索）                                       │
│    1  研究定义 — 主题初始化 + 问题分解 + 硬件探测        │
│    2  文献采集 — 检索策略 + 多源采集（5 个 API）         │
│    3  文献筛选 [门控]                                    │
│    4  知识抽取                                           │
│                                                          │
│  Ideation（构想）                                        │
│    5  假设综合 — 聚类发现 + 空白识别 + 假设生成          │
│    6  实验设计 [门控]                                    │
│    7  代码准备 — 硬件感知代码生成 + 资源规划             │
│                                                          │
│  Experimentation（实验）                                 │
│    8  实验执行 — 沙箱运行 + 迭代优化 + 自修复            │
│    9  分析决策 — 结果分析 + PIVOT/REFINE 自主决策        │
│                                                          │
│  Composition（撰写）                                     │
│   10  论文撰写 — 大纲 → 初稿 → 评审 → 修订              │
│                                                          │
│  Delivery（交付）                                        │
│   11  质量检查 [门控]                                    │
│   12  导出验证 — LaTeX 导出 + 引用审计 + 知识归档        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**关键设计：**

- **3 个门控阶段**（第 3、6、11 阶段）：支持人工审批介入，也可用 `--auto-approve` 自动通过。拒绝时自动回滚（3→2、6→5、11→10）。
- **2 个反馈循环**：第 9 阶段根据实验结果自主决策——PROCEED（继续）、REFINE（调参重跑，回到第 8 阶段）、PIVOT（假设不成立，回到第 5 阶段重新生成假设）。最多允许 2 次 PIVOT。
- **产物版本化**：每次 PIVOT/REFINE 自动快照之前的产物，确保决策演化完全可追溯。

### 3.2 阶段契约系统

每个阶段都有严格的**输入/输出契约**（`contracts.py`），定义：

| 契约字段 | 说明 |
|---------|------|
| `input_files` | 该阶段需要的前序产物文件列表 |
| `output_files` | 该阶段必须产出的文件列表 |
| `dod` | 完成标准（Definition of Done） |
| `error_code` | 失败时的错误码 |
| `max_retries` | 最大重试次数（如文献采集 2 次、代码生成 2 次） |

这保证了流水线的**确定性**——任何阶段的失败都有明确的错误码和重试策略，不会出现"跑到一半不知道哪里出了问题"的情况。

---

## 四、核心技术亮点

### 4.1 五源学术文献检索与三态熔断器

**这是 ScholarClaw 与所有"AI 写论文"工具的根本区别：我们不依赖 LLM 的记忆来生成引用，而是调用真实的学术数据库 API。**

#### 接入的 5 个学术 API

| API | 端点 | 用途 | 速率策略 |
|-----|------|------|---------|
| **arXiv** | `export.arxiv.org/api/query` | 预印本检索、arXiv ID 验证 | 3.1s 间隔，429 后 5.0s |
| **Semantic Scholar** | `api.semanticscholar.org/graph/v1` | 论文检索、批量获取（最多 500 条/次） | 1.5s（无 key）/ 0.3s（有 key） |
| **OpenAlex** | `api.openalex.org/works` | 广覆盖检索 | 0.2s 间隔，10K/天 |
| **CrossRef** | `api.crossref.org/works/{doi}` | DOI 验证 | 0.3s 间隔 |
| **DataCite** | `api.datacite.org/dois/{doi}` | arXiv DOI 验证（`10.48550/`、`10.5281/`） | 按需 |

#### 检索策略

- 默认检索顺序：**OpenAlex → Semantic Scholar → arXiv**（按覆盖率和速率限制优化）
- 自动查询扩展：LLM 生成更广泛的搜索词（综述、基准、变体），目标覆盖 30–60 篇参考文献
- 三级去重：DOI → arXiv ID → 模糊标题匹配（标题归一化后比对），冲突时保留引用数更高的记录

#### 三态熔断器（Circuit Breaker）

当某个 API 连续返回 429（限流）时，系统不会无限重试，而是启用**三态熔断器**：

```
CLOSED（正常）→ 连续 3 次 429 → OPEN（熔断，停止请求）
                                    ↓
                              冷却期（arXiv 180s / S2 120s）
                                    ↓
                              HALF_OPEN（试探性发送 1 个请求）
                                    ↓
                           成功 → CLOSED / 失败 → OPEN（冷却翻倍，上限 600s）
```

这意味着即使 Semantic Scholar 限流了，arXiv 和 OpenAlex 的结果仍然正常返回——**单个 API 的故障不会阻塞整条流水线**。

### 4.2 四层引用验证系统

**LLM 生成论文的最大风险是幻觉引用——编造不存在的论文。** ScholarClaw 在导出验证阶段（第 12 阶段），对每一条引用进行四层独立验证：

| 层级 | 验证方法 | 捕获的问题 | 判定逻辑 |
|------|---------|-----------|---------|
| **L1** | arXiv API `id_list` 查询 | 虚假的 arXiv ID | ID 不存在 → HALLUCINATED |
| **L2** | CrossRef DOI 解析 + DataCite 回退 | 无效 DOI、标题不匹配 | DOI 无法解析 → HALLUCINATED |
| **L3** | Semantic Scholar + arXiv 标题搜索 | 根本不存在的论文 | 标题相似度 < 0.50 → HALLUCINATED |
| **L4** | LLM 重评分 | 真实存在但与主题无关的凑数引用 | 相关性低 → LOW_RELEVANCE |

**判定阈值：**
- 标题相似度 ≥ 0.80 → VERIFIED（通过）
- 0.50 – 0.80 → SUSPICIOUS（可疑，保留但标记）
- < 0.50 → HALLUCINATED（幻觉，删除）

**相似度算法：** 词重叠 Jaccard 系数，分母取两个标题词集大小的最大值，避免短标题误判。

**自动清理：** 幻觉引用从论文正文的 `\cite{}` 中静默移除，`.bib` 文件中未被引用的条目自动精简。最终的 `references.bib` 仅包含经过验证的、被正文引用的参考文献。

**缓存机制：** 验证结果缓存在 `~/.cache/scholarclaw_engine/citation_verify/`，TTL 365 天，避免重复查询。

### 4.3 硬件感知的实验代码生成

ScholarClaw 不是生成一段"理论上能跑"的代码然后让用户自己解决环境问题。它在**研究定义阶段就探测本地硬件**，并据此调整后续所有阶段的代码生成策略：

| 硬件等级 | 探测方式 | 代码生成策略 |
|---------|---------|------------|
| **高性能** | `nvidia-smi` 检测到 ≥ 8 GB 显存 | 完整 PyTorch + CUDA 代码，缺少 torch 时自动安装 |
| **受限** | NVIDIA < 8 GB 或 Apple MPS | 轻量级实验（< 1M 参数、≤ 20 epochs），生成警告 |
| **纯 CPU** | 未检测到 GPU | 仅使用 NumPy / scikit-learn，不导入 torch |

**探测顺序：** NVIDIA（`nvidia-smi`）→ Apple MPS（`torch.backends.mps`）→ CPU fallback。

这意味着**同一个研究主题在 MacBook Air 和 A100 服务器上都能产出可运行的代码**——系统自动适配，用户无需手动调整。

### 4.4 五模式实验沙箱与自修复

#### 五种执行模式

| 模式 | 适用场景 | 特点 |
|------|---------|------|
| `simulated` | 快速原型验证 | 不执行代码，用数学公式生成模拟数据 |
| `sandbox` | 本地开发 | subprocess 执行，AST 校验 + import 白名单 |
| `docker` | 隔离执行 | Docker 容器，支持 GPU 直通，网络策略可配（`none` / `setup_only` / `pip_only` / `full`） |
| `ssh_remote` | 远程 GPU 服务器 | SSH 连接，指定 GPU ID |
| `colab_drive` | Google Colab | 通过 Google Drive 同步代码和结果 |

#### 安全沙箱机制

代码在执行前经过严格的**静态分析**：

- **AST 预检**：解析代码语法树，拒绝含有非白名单 import 的代码
- **禁止调用**：`os.system`、`subprocess.*`、`shutil.rmtree`、`eval`、`exec`、`compile`、`__import__` 等危险函数
- **禁止模块**：subprocess、shutil、socket、http、urllib、requests 等网络/系统模块
- **允许模块**：numpy、scipy、torch、sklearn、matplotlib、pandas 等科学计算库
- **内存限制**：可配置（默认 4,096 MB）
- **时间预算**：可配置（默认 300 秒）

#### 自修复机制

```
实验代码执行 → 失败
  ├─ 捕获完整 traceback
  ├─ 将 traceback + 原始代码发送给 LLM
  ├─ LLM 诊断根因，生成定向补丁
  ├─ 应用补丁，重新执行
  └─ 最多 3 轮修复（CodeAgent: exec_fix_max_iterations=3）
```

**额外保障：**
- **NaN/Inf 快速失败**：指标中出现 NaN 或 Inf 立即终止，不浪费计算资源
- **发散检测**：损失值 > 100 被标记为发散
- **部分结果捕获**：超时但已产出部分指标的实验标记为 `partial`，保留可用数据
- **配对统计**：自动计算 `mean_diff`、`std_diff`、`t_stat`、`p_value`、`ci95`

### 4.5 多智能体协作系统

ScholarClaw 内置三个专用智能体，各司其职：

#### CodeAgent（代码智能体）

| 参数 | 值 | 说明 |
|------|---|------|
| `exec_fix_max_iterations` | 3 | 执行失败后最多修复 3 轮 |
| `hard_validation_max_repairs` | 2 | AST 校验失败后最多修复 2 轮 |
| `tree_search_candidates` | 3 | 树搜索时生成 3 个候选方案 |
| `tree_search_max_depth` | 2 | 搜索深度 2 层 |
| `review_max_rounds` | 2 | 代码评审最多 2 轮 |

#### BenchmarkAgent（基准测试智能体）

自动从 HuggingFace 等平台获取相关基准数据集和 baseline 方法：

| 参数 | 值 | 说明 |
|------|---|------|
| `max_hf_results` | 10 | 最多检索 10 个 HuggingFace 数据集 |
| `min_benchmarks` | 1 | 至少 1 个基准数据集 |
| `min_baselines` | 2 | 至少 2 个 baseline 方法 |
| `max_iterations` | 2 | 最多迭代 2 轮 |

#### FigureAgent（图表智能体）

自动生成论文所需的可视化图表：

| 参数 | 值 | 说明 |
|------|---|------|
| `min_figures` | 3 | 每篇论文至少 3 张图 |
| `max_figures` | 8–10 | 最多 8–10 张图 |
| `dpi` | 300 | 出版级分辨率 |
| `render_timeout_sec` | 30 | 单张图渲染超时 30 秒 |
| `output_format` | python / latex | 支持 Python matplotlib 或 LaTeX tikz |

FigureAgent 还集成了 **Nano Banana**（基于 Gemini `gemini-2.5-flash-image`）用于 AI 辅助图表生成和质量评估。

### 4.6 多视角同行评审

论文初稿完成后，系统在撰写阶段内运行**结构化的多 Agent 评审**：

1. **方法论评审**：检查实验是否真正支撑了结论，标记缺失的 baseline，指出可复现性问题，评估统计有效性。
2. **表达力评审**：检查论证逻辑、未定义术语、图表描述、整体可读性。
3. **论文-证据一致性检查**：比对论文中描述的实验数量与实际运行数量——如果论文声称跑了 50 次实验但代码只跑了 5 次，会被标记。

评审按 NeurIPS/ICML 评分标准打分（1–10 分），覆盖 7 个维度。

**修订保障：**
- 修订稿若短于初稿，自动重试（防止 LLM 删减内容）
- "due to computational constraints" 等模糊表述最多出现 1 次
- 反免责声明强制：修订提示主动删除重复的模糊措辞

### 4.7 跨运行自学习（Evolution）

每次运行结束后，系统自动提取细粒度的经验教训：

- PIVOT/REFINE 决策的具体理由
- 实验 stderr 中的运行时警告（如 `RuntimeWarning: division by zero`）
- 指标异常（NaN、Inf、所有算法收敛速度异常一致）

这些教训以 JSONL 格式持久化存储，使用 **30 天半衰期的时间衰减加权**，作为 prompt overlay 注入未来运行。

可选集成 **MetaClaw**（跨运行知识迁移框架）：
- 将失败教训自动转化为可复用的 Skill 文件
- 注入后续运行的所有阶段
- 实测效果：阶段重试率降低 24.8%，REFINE 循环次数减少 40.0%

### 4.8 文献缓存与性能优化

| 缓存层 | 位置 | TTL |
|--------|------|-----|
| arXiv 检索结果 | `.scholarclaw_cache/literature/` | 24 小时 |
| Semantic Scholar 结果 | `.scholarclaw_cache/literature/` | 3 天 |
| OpenAlex 结果 | `.scholarclaw_cache/literature/` | 3 天 |
| 引用验证结果 | `~/.cache/scholarclaw_engine/citation_verify/` | 365 天 |

缓存键：`sha256(query|source|limit)[:16]`，避免重复请求，大幅降低 API 调用量。

---

## 五、技术指标与质量保障

### 5.1 测试覆盖

| 维度 | 数据 |
|------|------|
| 测试文件数 | 44 个 |
| 测试用例数 | 1,117+ |
| 覆盖模块 | 流水线执行器（100 例）、LaTeX 模板（70 例）、引用验证（46 例）、文献检索（46 例）、图表 Agent（45 例）、新颖性检测（37 例）、代码校验（36 例）、阶段逻辑（35 例）、健康检查（34 例）、进化学习（34 例）、Prompt 系统（34 例）等 |
| E2E 测试 | Docker 沙箱端到端、真实 LLM 端到端 |
| 回归测试 | 8 个专项回归用例 |

### 5.2 LLM 容错

| 机制 | 实现 |
|------|------|
| 模型回退链 | `primary_model` → `fallback_models`（可配置多级） |
| 请求重试 | 最多 3 次，指数退避（2s → 4s → 8s） |
| 多 Provider 支持 | OpenAI 兼容 API、Anthropic 原生适配、ACP 协议（Claude Code / Codex / Gemini / Kimi） |

### 5.3 安全机制

| 层面 | 措施 |
|------|------|
| 代码执行 | AST 静态分析 + import 白名单 + 危险函数黑名单 |
| 网络隔离 | Docker 模式支持 4 级网络策略（none / setup_only / pip_only / full） |
| 人工审批 | 3 个门控阶段（可配置） |
| 日志脱敏 | `redact_sensitive_logs: true` |
| 反数据捏造 | 实验无指标时硬性阻止论文撰写 |

---

## 六、与同类项目的差异化

| 维度 | 通用 LLM 直接写 | ScholarClaw |
|------|-----------------|-------------|
| 文献来源 | LLM 记忆（易幻觉） | **5 个真实学术 API 实时检索** |
| 引用验证 | 无 | **四层独立验证** |
| 实验执行 | 不执行 | **5 种模式 + 自修复** |
| 硬件适配 | 无 | **自动探测 GPU/MPS/CPU** |
| 反馈循环 | 无 | **PIVOT/REFINE 自主决策** |
| 会议模板 | 无 | **6 套会议模板** |
| 同行评审 | 无 | **多 Agent 结构化评审** |
| 跨运行学习 | 无 | **Evolution 自学习** |
| 测试覆盖 | N/A | **1,117+ 测试用例** |

---

## 七、应用场景

### 7.1 科研加速

- **研究生/博士生**：快速生成研究方向的初步探索论文，作为正式研究的起点和文献综述基础
- **跨领域研究者**：进入不熟悉的领域时，快速了解该领域的核心问题、方法和前沿进展
- **实验室组会**：一键生成某个主题的结构化分析，作为讨论材料

### 7.2 教育辅助

- **学术写作教学**：展示一篇合格学术论文的完整结构和写作规范
- **实验设计教学**：展示从假设到实验到分析的完整科学方法流程
- **批判性思维训练**：利用自动评审功能，让学生学习如何评审论文

### 7.3 产业研发

- **技术调研**：快速生成某个技术方向的结构化分析报告
- **专利前期调研**：系统性检索和分析相关文献
- **竞品技术分析**：基于公开论文的技术对比分析

---

## 八、技术栈

| 层面 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| 包管理 | pip / hatch（`pyproject.toml`） |
| LLM 接口 | OpenAI 兼容 API、Anthropic 原生、ACP 协议 |
| 学术 API | arXiv API、Semantic Scholar API v1、OpenAlex API、CrossRef API、DataCite API |
| 实验执行 | subprocess（沙箱）、Docker SDK、paramiko（SSH）、Google Drive API（Colab） |
| LaTeX | 自研 Markdown → LaTeX 转换器，支持数学公式、表格、图片、交叉引用、`\cite{}` |
| 图表生成 | matplotlib（Python）、tikz（LaTeX）、Nano Banana（Gemini AI） |
| 测试 | pytest，1,117+ 用例 |
| 配置 | YAML，200+ 可配参数 |

---

## 九、项目现状与路线图

### 当前版本：v0.5.0

- 12 阶段 / 5 阶段组流水线完整可用
- 5 个学术 API 接入
- 四层引用验证
- 5 种实验执行模式
- 6 套会议模板
- 3 个专用智能体（Code / Benchmark / Figure）
- 跨运行自学习（Evolution）
- 1,117+ 测试用例
- 中英文文档

### 后续规划

| 阶段 | 内容 |
|------|------|
| v0.6 | 支持更多会议模板（ACL、EMNLP、AAAI）；增加中文论文生成能力 |
| v0.7 | 集成更多文献源（PubMed、IEEE Xplore）；支持综述论文（survey）生成 |
| v0.8 | 多论文并行生成；实验结果跨论文复用 |
| v1.0 | Web UI；团队协作模式；论文版本管理 |

---

## 十、ScholarClaw 与 OpenClaw 的集成架构

ScholarClaw 不是一个孤立的命令行工具——它被设计为 **OpenClaw 生态系统的原生技能（Skill）**，通过 OpenClaw 的技能发现机制、适配器协议和消息通道与用户交互。

### 10.1 技能发现：用户说一句话，OpenClaw 自动调度

OpenClaw 的技能系统通过扫描 `skills/<name>/SKILL.md` 文件来发现可用技能。ScholarClaw 在 `skills/scholarclaw/SKILL.md` 中声明了自己的触发条件：

```
触发条件：
- 用户说 "research [topic]"、"write a paper about [topic]"、"investigate [topic]"
- 用户要求运行自主研究流水线
- 用户要求从零生成研究论文
- 用户直接提到 "ScholarClaw"
```

当用户在 OpenClaw 的任何消息通道（Telegram、Discord、Slack、Web、iMessage 等）中发送类似消息时，OpenClaw 的技能匹配系统将消息路由到 ScholarClaw。具体流程：

1. **用户发送消息**：在任意通道中说"帮我研究注意力机制在时序预测中的效率"
2. **消息进入 OpenClaw**：经由 Telegram / Discord / Slack / Web 等通道的消息入口
3. **技能匹配**：`resolveSkillCommandInvocation` 引擎匹配到 `/scholarclaw` 命令，或 LLM 根据系统提示中注入的 SKILL.md 内容自主判断应使用 ScholarClaw
4. **消息改写**：消息体被改写为 `"Use the scholarclaw skill for this request. User input: ..."`
5. **Agent 执行**：
   - 读取 SKILL.md，理解安装和运行方式
   - 检查环境（venv、依赖是否就绪）
   - 运行 `scholarclaw run --topic "..." --auto-approve`
6. **结果返回**：Agent 收集产出物，通过用户所在的消息通道返回

**用户不需要知道 ScholarClaw 的存在**——他们只需要对 OpenClaw 说"帮我研究 X"，OpenClaw 自动完成克隆、安装、配置、执行和结果返回。

### 10.2 六端口适配器协议：OpenClaw 能力的按需注入

ScholarClaw 定义了 6 个**类型化适配器协议**（`adapters.py`），每个协议对应 OpenClaw 的一种平台能力。当 OpenClaw 提供某种能力时，ScholarClaw 自动消费；当能力不可用时，流水线照常运行——**零耦合，按需增强**。

| 适配器 | 协议接口 | OpenClaw 提供的能力 | 流水线中的用途 |
|--------|---------|-------------------|--------------|
| **CronAdapter** | `schedule_resume(run_id, stage_id, reason) → str` | 定时任务调度 | 安排流水线在指定时间恢复执行（如隔夜跑长实验） |
| **MessageAdapter** | `notify(channel, subject, body) → str` | 消息推送（Discord/Slack/Telegram） | 阶段开始时通知、门控审批请求推送 |
| **MemoryAdapter** | `append(namespace, content) → str` | 跨会话持久化记忆 | 记录阶段状态到 `stages` 命名空间、门控决策到 `gates` 命名空间 |
| **SessionsAdapter** | `spawn(name, command) → str` | 并行子会话 | 为并发阶段派生独立执行环境 |
| **WebFetchAdapter** | `fetch(url) → FetchResponse` | 网页抓取 | 文献采集阶段验证文献源可用性 |
| **BrowserAdapter** | `open(url) → BrowserPage` | 浏览器自动化 | 采集需要 JavaScript 渲染的论文页面 |

代码级证据——消息通知（`executor.py`）：

```python
# 阶段开始时，通过 OpenClaw 的消息通道通知用户
if bridge.use_message and config.notifications.on_stage_start:
    adapters.message.notify(
        config.notifications.channel,
        f"stage-{int(stage):02d}-start",
        f"Starting {stage.name}",
    )

# 门控阶段需要审批时，推送审批请求
if bridge.use_message and config.notifications.on_gate_required:
    adapters.message.notify(
        config.notifications.channel,
        f"gate-{int(stage):02d}",
        f"Approval required for {stage.name}",
    )
```

代码级证据——跨会话记忆（`executor.py`）：

```python
# 将阶段运行状态持久化到 OpenClaw 的记忆系统
if bridge.use_memory:
    adapters.memory.append("stages", f"{run_id}:{int(stage)}:running")
    # ... 阶段完成后 ...
    adapters.memory.append("stages", f"{run_id}:{int(stage)}:{result.status.value}")
```

代码级证据——网页抓取验证（`executor.py`）：

```python
# 文献采集阶段：利用 OpenClaw 的 web_fetch 能力验证文献源
if config.openclaw_bridge.use_web_fetch:
    for src in sources:
        response = adapters.web_fetch.fetch(str(src.get("url", "")))
        src["status"] = (
            "verified" if response.status_code in (200, 301, 302, 405)
            else "unreachable"
        )
```

这种设计意味着：
- **独立运行时**（CLI 模式）：使用默认的 Recording 实现，流水线完全自包含
- **OpenClaw 内运行时**：OpenClaw 注入真实的适配器实现，ScholarClaw 自动获得消息推送、记忆持久化、网页抓取等增强能力

### 10.3 论文导出通道：从研究产物到用户手中

ScholarClaw 的产出物通过 OpenClaw 的多通道消息系统返回给用户：

1. **流水线完成**：产出物写入 `artifacts/sc-YYYYMMDD-HHMMSS-<hash>/` 目录

| 产出文件 | 内容 |
|---------|------|
| `deliverables/paper.tex` | LaTeX 源文件 |
| `deliverables/paper.pdf` | 自动编译的 PDF（需要 `pdflatex`） |
| `deliverables/references.bib` | 验证过的引用 |
| `paper_draft.md` | Markdown 初稿 |
| `peer_review.md` | 评审报告 |
| `verification_report.json` | 引用审计记录 |

2. **Agent 汇总**：OpenClaw Agent 读取产出目录，提取关键信息
3. **多通道分发**：根据用户所在通道选择合适的返回方式

| 通道 | 返回形式 |
|------|---------|
| Telegram / Discord / Slack | 发送摘要文本 + 关键文件附件 |
| Web UI | 展示完整产出目录，支持在线预览 |
| CLI | 打印产出路径 |

OpenClaw 还内置了 `/export-paper` 命令（`commands-export-paper.ts`），可以将会话中的学术内容导出为格式化的 HTML 或 PDF 报告，与 ScholarClaw 的 Markdown 产出无缝衔接。

### 10.4 与 OpenClaw 其他研究技能的协作

ScholarClaw 在 OpenClaw 生态中并非孤立存在，它与其他研究类技能形成互补：

| 技能 | 定位 | 与 ScholarClaw 的关系 |
|------|------|---------------------|
| **academic-lobster** | 轻量级学术分析——输入主题或 PDF，输出结构化研究报告 | ScholarClaw 的"轻量替代"：不跑实验，不生成 LaTeX，但速度快、适合初步探索 |
| **scientific-lobster** | 科学研究流水线——文献综述、假设、实验设计 | ScholarClaw 的"轻量版"：ScholarClaw 在此基础上增加了代码执行、自修复、引用验证 |
| **ScholarClaw** | 全自主研究引擎——从想法到可编译论文 | 完整版：真实文献 API、沙箱实验、四层引用验证、会议级 LaTeX |

用户可以根据需求选择不同深度的研究工具：
- 快速了解一个领域 → `academic-lobster`（分钟级）
- 结构化研究分析 → `scientific-lobster`（小时级）
- 完整论文生成 → `ScholarClaw`（数小时级）

### 10.5 ACP 协议：无 API Key 的 Agent 互操作

ScholarClaw 通过 **ACP（Agent Client Protocol）** 支持以任何兼容的 AI 编码助手作为 LLM 后端，无需单独配置 API Key：

```yaml
llm:
  provider: "acp"
  acp:
    agent: "claude"    # 或 codex / gemini / kimi / opencode
    cwd: "."
```

ACP 客户端（`acp_client.py`）通过 OpenClaw 的 `acpx` 扩展（位于 `~/.openclaw/extensions/acpx`）与 Agent 通信，维持**单一持久会话**贯穿全部阶段——Agent 在整个流水线执行过程中保持完整的上下文，不会因为阶段切换而丢失信息。

| Agent | CLI 命令 | 提供方 |
|-------|---------|--------|
| Claude Code | `claude` | Anthropic |
| Codex CLI | `codex` | OpenAI |
| Gemini CLI | `gemini` | Google |
| OpenCode | `opencode` | SST |
| Kimi CLI | `kimi` | Moonshot |

---

## 十一、团队与开源

- **开源协议**：MIT License
- **代码仓库**：[github.com/Randy-sin/ScholarClaw](https://github.com/Randy-sin/ScholarClaw)
- **技术文档**：中英文双语，含集成指南、测试指南、配置参考

---

## 十二、总结与愿景

### 我们做了什么

学术研究的核心价值在于**思考**——提出问题、构建假设、解释世界。但在现实中，一个研究者超过 70% 的时间花在了思考之外的事情上：在五个平台之间搜文献、调试实验环境的 CUDA 版本、手动核对每一条 BibTeX 是否真实、和 LaTeX 的排版错误搏斗。

ScholarClaw 的出发点很简单：**把研究者从流程性劳动中解放出来，让他们把时间还给真正的智力工作。**

我们用 12 个阶段、5 个学术 API、四层引用验证、五模式实验沙箱和三个专用智能体，构建了一条从"一句话"到"一篇可编译论文"的完整流水线。这不是一个玩具 demo——它有 1,117 个测试用例、200+ 可配参数、完整的错误恢复机制和跨运行的自学习能力。

### 我们解决了什么问题

| 传统方式 | ScholarClaw |
|---------|-------------|
| 文献检索靠人工搜索 + 记忆 | 5 个学术 API 实时检索，三态熔断器保障可用性 |
| 引用真实性靠人眼核对 | 四层自动验证，幻觉引用零容忍 |
| 实验代码靠手写 + 手调 | 硬件感知代码生成 + 自修复沙箱 |
| 论文格式靠反复排版 | 一键输出 6 套会议模板的可编译 LaTeX |
| 各环节之间靠人工衔接 | 确定性流水线，带门控、回滚和反馈循环 |

### 为什么它属于 OpenClaw 生态

ScholarClaw 不是一个独立的工具，而是 OpenClaw 平台能力的一次**纵深延伸**。

OpenClaw 提供了消息通道、记忆系统、定时调度、浏览器自动化等基础设施；ScholarClaw 通过六端口适配器协议按需消费这些能力，将"对话式 AI 助手"升级为"对话式研究助手"。用户不需要学习新工具、不需要切换界面——在他们已经熟悉的 Telegram、Discord 或 Web 聊天窗口中，说一句"帮我研究 X"，就能启动一条完整的研究流水线。

这体现了 OpenClaw 生态的核心理念：**AI 不应该是一个需要你去适应的工具，而应该是一个融入你现有工作流的伙伴。**

### 更远的未来

ScholarClaw 当前解决的是"从 0 到 1"的问题——从一个想法到一篇初稿。但学术研究的完整生命周期远不止于此：

- **从 1 到 N**：同一个研究方向的多篇论文之间，实验结果能否复用？文献库能否共享？假设能否演化？
- **从个人到团队**：多个研究者能否在同一条流水线上协作，各自负责不同阶段？
- **从英文到多语言**：中文学术论文有自己的写作规范和期刊模板，能否原生支持？
- **从 ML 到全学科**：当前的实验沙箱偏向机器学习，但化学、生物、社会科学的实验范式完全不同。

这些问题定义了 ScholarClaw 的下一程。我们相信，**自主研究引擎不会取代研究者，但它会重新定义研究者的时间分配**——让人类把最宝贵的认知资源投入到只有人类才能做的事情上：提出真正重要的问题。

---

<p align="center">
<b>ScholarClaw：让研究回归思考本身。</b>
</p>
