<p align="center">
  <img src="../image/banner.png" width="680" alt="ScholarClaw">
</p>

<p align="center">
  <strong>一个想法进去，一篇论文出来。23 阶段全自主研究引擎。零幻觉引用。</strong>
</p>

<p align="center">
  <a href="https://github.com/Randy-sin/ScholarClaw/stargazers"><img src="https://img.shields.io/github/stars/Randy-sin/ScholarClaw?style=social" alt="GitHub Stars"></a>&nbsp;
  <a href="https://github.com/Randy-sin/ScholarClaw/network/members"><img src="https://img.shields.io/github/forks/Randy-sin/ScholarClaw?style=social" alt="Forks"></a>&nbsp;
  <a href="https://github.com/Randy-sin/ScholarClaw/issues"><img src="https://img.shields.io/github/issues/Randy-sin/ScholarClaw?color=orange" alt="Issues"></a>&nbsp;
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>&nbsp;
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white" alt="Python 3.11+"></a>
</p>

<p align="center">
  <a href="#-快速开始">快速开始</a> •
  <a href="#-工作原理">工作原理</a> •
  <a href="#-核心能力">核心能力</a> •
  <a href="#%EF%B8%8F-配置">配置</a> •
  <a href="../README.md">English</a>
</p>

---

> **ScholarClaw** 接收一个研究主题，自主产出一篇会议级学术论文——真实文献来自 arXiv、Semantic Scholar 和 OpenAlex，实验在沙箱中实际运行，多 Agent 同行评审，最终输出可直接编译的 NeurIPS / ICML / ICLR LaTeX。

---

## ✨ 亮点

<table>
<tr>
<td width="50%">

**🔬 真正的研究，不是摘要拼凑**

调用真实学术 API（arXiv、Semantic Scholar、OpenAlex），在沙箱中运行实际实验，四层流水线验证每一条引用。

</td>
<td width="50%">

**🧠 自修复 & 自转向**

实验崩溃时自动诊断修复。假设不成立时自主 PIVOT 到新研究方向——全程无需人工介入。

</td>
</tr>
<tr>
<td width="50%">

**📝 会议级产出**

生成 5,000–6,500 词论文，LaTeX 适配 NeurIPS、ICML 或 ICLR。把 `deliverables/` 上传 Overleaf 直接编译。

</td>
<td width="50%">

**🛡️ 零幻觉引用**

四层引用验证：arXiv ID 检查 → CrossRef/DataCite DOI → Semantic Scholar 模糊匹配 → LLM 相关性评分。假引用直接删除。

</td>
</tr>
</table>

---

## 📦 产出物

```
scholarclaw run --topic "长序列时序 Transformer 中的高效注意力机制"
```

```
artifacts/sc-20260318-143022-a7f3/
├── deliverables/
│   ├── paper.tex              # 会议级 LaTeX
│   ├── references.bib         # 验证过的 BibTeX（零幻觉）
│   ├── neurips_2025.sty       # 模板样式文件
│   └── figures/               # 自动生成的图表
├── paper_draft.md             # 完整 Markdown 论文（8 个章节）
├── experiments/
│   ├── run_001/               # 代码 + 输出 + metrics.json
│   ├── run_002/               # 自修复重试
│   └── comparison_charts/     # 误差线、置信区间
├── peer_review.md             # 多 Agent 评审（方法论 + 表达力）
├── verification_report.json   # 四层引用完整性审计
└── evolution/                 # 本次运行提取的经验教训
```

---

## 🚀 快速开始

```bash
# 1️⃣  克隆
git clone https://github.com/Randy-sin/ScholarClaw.git
cd ScholarClaw

# 2️⃣  安装
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# 3️⃣  配置
cp config.scholarclaw.example.yaml config.scholarclaw.yaml
# → 编辑 config.scholarclaw.yaml：填入你的 LLM API Key

# 4️⃣  运行
export OPENAI_API_KEY="sk-..."
scholarclaw run --topic "你的研究主题" --auto-approve
```

<details>
<summary><b>📋 最小配置文件</b></summary>

```yaml
project:
  name: "my-research"

research:
  topic: "你的研究主题"

llm:
  base_url: "https://api.openai.com/v1"
  api_key_env: "OPENAI_API_KEY"
  primary_model: "gpt-4o"
  fallback_models: ["gpt-4o-mini"]

experiment:
  mode: "sandbox"
  sandbox:
    python_path: ".venv/bin/python"
```

</details>

---

## 🔬 工作原理

**23 个阶段，8 个阶段组。** 门控阶段暂停等待确认（`--auto-approve` 跳过）。

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  阶段组 A ─ 研究定义                阶段组 E ─ 实验执行             │
│    1  TOPIC_INIT                      12  EXPERIMENT_RUN            │
│    2  PROBLEM_DECOMPOSE               13  ITERATIVE_REFINE  ← 修复 │
│                                                                     │
│  阶段组 B ─ 文献发现                阶段组 F ─ 分析与决策           │
│    3  SEARCH_STRATEGY                 14  RESULT_ANALYSIS   ← 多Agent│
│    4  LITERATURE_COLLECT  ← API       15  RESEARCH_DECISION ← 转向 │
│    5  LITERATURE_SCREEN   [门控]                                    │
│    6  KNOWLEDGE_EXTRACT             阶段组 G ─ 论文撰写             │
│                                       16  PAPER_OUTLINE             │
│  阶段组 C ─ 知识综合                  17  PAPER_DRAFT               │
│    7  SYNTHESIS                       18  PEER_REVIEW      ← 审查  │
│    8  HYPOTHESIS_GEN      ← 辩论    19  PAPER_REVISION             │
│                                                                     │
│  阶段组 D ─ 实验设计                阶段组 H ─ 终稿                 │
│    9  EXPERIMENT_DESIGN   [门控]      20  QUALITY_GATE     [门控]  │
│   10  CODE_GENERATION                 21  KNOWLEDGE_ARCHIVE         │
│   11  RESOURCE_PLANNING               22  EXPORT_PUBLISH   ← LaTeX │
│                                       23  CITATION_VERIFY  ← 四层  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

> **决策循环：** 第 15 阶段评估结果后自主决定 **PROCEED**、**REFINE**（→ 第 13 阶段）或 **PIVOT**（→ 第 8 阶段）。所有产物自动版本化。

---

## 🎯 核心能力

### 📚 来自真实 API 的文献

| 数据源 | 提供内容 | 速率限制 |
|--------|---------|---------|
| **arXiv API** | 全文搜索、PDF 链接、元数据 | 无限制 |
| **Semantic Scholar** | 标题、DOI、引用数、摘要 | 100 次/5分钟（免费） |
| **OpenAlex** | 广覆盖、机构数据 | 宽松 |

自动去重：DOI → arXiv ID → 模糊标题匹配。API 故障时断路器自动降级。

### 🔍 四层引用验证

终稿中的每条引用都经过：

| 层级 | 方法 | 捕获问题 |
|------|------|---------|
| **L1** | arXiv API 查询 | 虚假 arXiv ID |
| **L2** | CrossRef + DataCite | 无效 DOI、标题不匹配 |
| **L3** | Semantic Scholar | 不存在的论文（模糊匹配 ≥0.80） |
| **L4** | LLM 相关性评分 | 真实但不相关的凑数引用 |

验证失败的引用自动删除。`.bib` 中未被引用的条目自动精简。

### 🖥️ 硬件感知实验

自动检测计算环境，据此调整生成的代码：

| 等级 | 检测方式 | 生成代码 |
|------|---------|---------|
| **高性能** | NVIDIA GPU ≥8 GB | 完整 PyTorch + CUDA |
| **受限** | NVIDIA <8 GB / Apple MPS | 轻量模型、小 batch |
| **纯 CPU** | 无 GPU | NumPy + scikit-learn |

### 🔧 自修复执行

```
代码运行 → 失败？
  ├─ 读取 traceback
  ├─ LLM 诊断根因
  ├─ 生成定向补丁
  ├─ 重跑（最多 3 轮）
  └─ 超时时捕获部分结果
```

沙箱特性：AST 校验、import 白名单、NaN/Inf 检测、内存限制。

### 🤖 多 Agent 同行评审

| 评审者 | 关注点 |
|--------|--------|
| **方法论 Agent** | 实验充分性、混淆因素、可复现性、统计有效性 |
| **表达力 Agent** | 论证逻辑、术语定义、图表描述、可读性 |

加上**论文-证据一致性检查**：论文声称跑了 N 次实验但代码只跑了 M 次？会被标记。

### 🔄 PIVOT / REFINE 决策循环

| 决策 | 触发条件 | 动作 |
|------|---------|------|
| **PROCEED** | 结果支持假设 | 继续写论文 |
| **REFINE** | 有前景但噪声大 | 调参 → 重跑实验 |
| **PIVOT** | 假设不成立 | 重新生成假设 → 重启 |

每次循环自动版本化所有产物，保证完整可追溯。

---

## 📐 会议模板

| 会议 | 配置值 | 分栏 |
|------|-------|------|
| NeurIPS 2025 | `neurips_2025` | 单栏 |
| ICLR 2026 | `iclr_2026` | 单栏 |
| ICML 2026 | `icml_2026` | 双栏 |

```yaml
export:
  target_conference: "neurips_2025"
```

`deliverables/` 包含 `.sty`、`.bst`、`.cls` 文件，上传 Overleaf 直接编译。

---

## ⚙️ 配置

<details>
<summary><b>完整配置参考（点击展开）</b></summary>

```yaml
# ─── 项目 ───
project:
  name: "my-research"
  mode: "full-auto"                  # docs-first | semi-auto | full-auto

# ─── 研究 ───
research:
  topic: "..."
  domains: ["ml", "nlp"]
  daily_paper_count: 8
  quality_threshold: 4.0

# ─── LLM ───
llm:
  provider: "openai-compatible"      # 或 "acp"
  base_url: "https://api.openai.com/v1"
  api_key_env: "OPENAI_API_KEY"
  primary_model: "gpt-4o"
  fallback_models: ["gpt-4o-mini"]
  acp:
    agent: "claude"                  # claude | codex | gemini | kimi
    cwd: "."

# ─── 实验 ───
experiment:
  mode: "sandbox"                    # simulated | sandbox | docker | ssh_remote
  time_budget_sec: 300
  max_iterations: 10
  metric_key: "val_loss"
  metric_direction: "minimize"
  sandbox:
    python_path: ".venv/bin/python"
    gpu_required: false
    allowed_imports: [math, random, json, csv, numpy, torch, sklearn]
    max_memory_mb: 4096
  docker:
    image: "scholarclaw/experiment:latest"
    network_policy: "setup_only"
    gpu_enabled: true
  ssh_remote:
    host: ""
    gpu_ids: []

# ─── 导出 ───
export:
  target_conference: "neurips_2025"
  authors: "Anonymous"

# ─── 质量门控 ───
security:
  hitl_required_stages: [5, 9, 20]
  allow_publish_without_approval: false

# ─── 跨运行学习（可选）───
metaclaw_bridge:
  enabled: false
  skills_dir: "~/.metaclaw/skills"
```

</details>

---

## 🛠️ 命令行

```bash
# 完整流水线
scholarclaw run --topic "..." --auto-approve

# 指定配置
scholarclaw run --config config.scholarclaw.yaml --topic "..."

# 从指定阶段恢复
scholarclaw run --from-stage PAPER_OUTLINE --auto-approve

# 仅验证配置
scholarclaw validate --config config.scholarclaw.yaml
```

---

## 🗂️ 项目结构

```
scholarclaw_engine/
├── pipeline/           # 阶段运行器、执行器、契约
├── literature/         # arXiv、Semantic Scholar、OpenAlex 客户端
├── experiment/         # 沙箱、Docker、SSH、自修复
├── agents/             # CodeAgent、BenchmarkAgent、FigureAgent
├── templates/styles/   # NeurIPS / ICML / ICLR LaTeX 模板
├── llm/                # LLM 适配器（OpenAI 兼容、ACP）
├── metaclaw_bridge/    # 跨运行学习（可选）
└── knowledge/          # 结构化知识库

tests/                  # 测试套件
docs/                   # 中英文文档
```

---

## 🤝 贡献

欢迎贡献！请先开 issue 讨论你想做的改动。

```bash
# 开发环境
git clone https://github.com/Randy-sin/ScholarClaw.git
cd ScholarClaw
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v
```

---

## 📄 许可证

[MIT](../LICENSE) — 随便用。

---

<p align="center">
  <sub>Built with 🦞 by ScholarClaw contributors</sub>
</p>
