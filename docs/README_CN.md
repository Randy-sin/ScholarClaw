<p align="center">
  <img src="../image/banner.png" width="680" alt="ScholarClaw">
</p>

<p align="center">
  <a href="https://github.com/Randy-sin/ScholarClaw/stargazers"><img src="https://img.shields.io/github/stars/Randy-sin/ScholarClaw?style=social" alt="Stars"></a>&nbsp;
  <a href="https://github.com/Randy-sin/ScholarClaw/network/members"><img src="https://img.shields.io/github/forks/Randy-sin/ScholarClaw?style=social" alt="Forks"></a>&nbsp;
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT"></a>&nbsp;
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" alt="Python"></a>
</p>

<p align="center">
  <a href="#上手">上手</a> &middot;
  <a href="#内部机制">内部机制</a> &middot;
  <a href="#引用可信度">引用可信度</a> &middot;
  <a href="../README.md">📖 English Docs / 英文文档</a>
</p>

---

ScholarClaw 是一个端到端的学术研究自动化引擎。
你用自然语言描述一个研究方向，它返回一篇论文初稿、真实的参考文献、已执行的实验代码，以及可以直接在 Overleaf 上编译的 LaTeX。

**它解决的问题：** 写一篇学术论文涉及大量繁琐且容易出错的步骤——检索文献、设计实验、跑代码、整理引用、排版 LaTeX。ScholarClaw 把这些步骤串成一条确定性流水线，让你可以专注于想法本身，而不是流程上的杂活。

---

## 上手

```bash
git clone https://github.com/Randy-sin/ScholarClaw.git && cd ScholarClaw
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp config.scholarclaw.example.yaml config.scholarclaw.yaml   # 编辑：填入你的 API Key
scholarclaw run --topic "你的研究问题" --auto-approve
```

结果在 `artifacts/` 目录下。`deliverables/` 子目录可以直接上传 Overleaf 编译。

<details>
<summary>最小 YAML 配置</summary>

```yaml
project:
  name: "my-project"
research:
  topic: "你的研究主题"
llm:
  base_url: "https://api.openai.com/v1"
  api_key_env: "OPENAI_API_KEY"
  primary_model: "gpt-4o"
experiment:
  mode: "sandbox"
  sandbox:
    python_path: ".venv/bin/python"
```
</details>

---

## 产出物

一次运行产生一个自包含的研究产物：

| 文件 | 说明 |
|------|------|
| `paper_draft.md` | 5 000 – 6 500 词的完整初稿，从引言到结论 |
| `paper.tex` + `*.sty` | 可编译的 LaTeX（NeurIPS / ICML / ICLR） |
| `paper.pdf` | 自动编译的 PDF *（需要安装 `pdflatex`，见下方说明）* |
| `references.bib` | 每条引用都经过在线数据库验证的 BibTeX |
| `experiments/` | 生成的 Python 代码、运行日志、`metrics.json` |
| `charts/` | 带误差线的对比图表 |
| `peer_review.md` | 自动评审（方法论 + 表达力） |
| `verification_report.json` | 逐条引用的审计记录 |

> **PDF 生成说明：** 如果系统安装了 `pdflatex`，流水线会自动将 `paper.tex` 编译为 `paper.pdf`（遇到常见 LaTeX 错误最多自动修复 3 次）。如果未安装 `pdflatex`，流水线仍会正常完成，输出 `.tex` + `.bib` 文件——你可以在 [Overleaf](https://overleaf.com) 上编译，或使用本地 TeX 发行版（macOS: `brew install --cask mactex`，Ubuntu: `sudo apt install texlive-full`，或轻量替代方案 [tectonic](https://tectonic-typesetting.github.io/)）。

---

## 内部机制

流水线按**关注点**划分为五个阶段组：

```
 探索       → 定义问题、检索文献、筛选、提取知识
 构想       → 综合发现、形成假设、设计实验、生成代码
 实验       → 沙箱运行、自动修复、分析结果、决定：继续或转向
 撰写       → 初稿、同行评审、修订
 交付       → 质量检查、LaTeX 导出、引用审计
```

两个反馈循环防止流水线跑偏：

- **调整** — 结果有前景但噪声大 → 调参，重跑实验。
- **转向** — 假设不成立 → 生成新假设，从综合阶段重启。

每次循环都会快照所有产物，不会丢失任何东西。

---

## 引用可信度

LLM 生成论文的最大风险是虚假引用。ScholarClaw 在初稿完成后用多轮验证来应对：

| 轮次 | 数据源 | 捕获的问题 |
|------|--------|-----------|
| 1 | arXiv API | 不存在的 arXiv 标识符 |
| 2 | CrossRef / DataCite | 无法解析的 DOI 或标题不匹配 |
| 3 | Semantic Scholar | 根本不存在的论文（模糊标题匹配 ≥ 0.80） |
| 4 | LLM 重评分 | 真实存在但与主题无关的凑数引用 |

任何一轮未通过的引用会从 `.bib` 和正文 `\cite{}` 中移除。审计记录保存在 `verification_report.json`。

---

## 硬件适配

生成实验代码前，ScholarClaw 会探测本地环境：

| 检测到 | 策略 |
|--------|------|
| NVIDIA GPU ≥ 8 GB | 完整 PyTorch + CUDA |
| NVIDIA < 8 GB 或 Apple MPS | 轻量模型、小 batch |
| 纯 CPU | NumPy / scikit-learn |

同一个主题在 MacBook Air 和多卡服务器上都能产出可运行的代码——流水线自动适配。

---

## 实验沙箱

生成的代码在受限沙箱中运行：

- **AST 预检** — 执行前拒绝含有非白名单 import 的代码。
- **发散守卫** — 提前终止产出 NaN / Inf 的运行。
- **自动修复** — 失败时把 traceback 反馈给 LLM，生成定向补丁。最多 3 轮修复。
- **部分捕获** — 超时时，已收集的指标仍然保存。

---

## 自动评审

初稿完成后自动运行两轮评审：

1. **方法论** — 检查实验是否真正支撑了结论，标记缺失的 baseline，指出可复现性问题。
2. **表达力** — 检查论证逻辑、未定义术语、图表描述。

额外的一致性检查会比对论文中描述的实验数量与实际运行数量。

---

## LaTeX 模板

| 目标 | 配置值 | 说明 |
|------|-------|------|
| NeurIPS 2025 | `neurips_2025` | 单栏 |
| ICLR 2026 | `iclr_2026` | 单栏 |
| ICML 2026 | `icml_2026` | 双栏 |

```yaml
export:
  target_conference: "neurips_2025"
```

样式文件（`.sty`、`.bst`、`.cls`）打包在 `deliverables/` 中，上传 Overleaf 直接编译。

---

## 配置

<details>
<summary>完整参考</summary>

```yaml
project:
  name: "my-research"
  mode: "full-auto"              # docs-first | semi-auto | full-auto

research:
  topic: "..."
  domains: ["ml", "nlp"]

llm:
  provider: "openai-compatible"  # 或 "acp"
  base_url: "https://api.openai.com/v1"
  api_key_env: "OPENAI_API_KEY"
  primary_model: "gpt-4o"
  fallback_models: ["gpt-4o-mini"]
  acp:
    agent: "claude"
    cwd: "."

experiment:
  mode: "sandbox"                # simulated | sandbox | docker | ssh_remote
  time_budget_sec: 300
  max_iterations: 10
  sandbox:
    python_path: ".venv/bin/python"
    allowed_imports: [math, random, json, csv, numpy, torch, sklearn]
    max_memory_mb: 4096
  docker:
    image: "scholarclaw/experiment:latest"
    network_policy: "setup_only"
  ssh_remote:
    host: ""
    gpu_ids: []

export:
  target_conference: "neurips_2025"
  authors: "Anonymous"

security:
  hitl_required_stages: [3, 6, 11]
  allow_publish_without_approval: false
```
</details>

---

## 命令行

```bash
scholarclaw run --topic "..." --auto-approve          # 完整流水线
scholarclaw run --config my.yaml --topic "..."        # 自定义配置
scholarclaw run --from-stage PAPER_WRITE               # 从中间阶段恢复
scholarclaw validate --config my.yaml                  # 仅验证配置
```

---

## 目录结构

```
scholarclaw_engine/
  pipeline/         阶段运行器 + 执行器
  literature/       arXiv、Semantic Scholar、OpenAlex 客户端
  experiment/       沙箱、Docker、SSH、自动修复
  agents/           CodeAgent、BenchmarkAgent、FigureAgent
  templates/        NeurIPS / ICML / ICLR LaTeX 样式
  llm/              LLM 适配器
  knowledge/        结构化知识库
tests/
docs/               中英文文档
```

---

## 贡献

欢迎 PR——请先开 issue 讨论范围。

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

---

## 许可证

MIT — 见 [LICENSE](../LICENSE)。

<p align="center"><sub>🦞</sub></p>
