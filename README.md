<p align="center">
  <img src="image/banner.png" width="680" alt="ScholarClaw">
</p>

<p align="center">
  <strong>From idea to paper. Fully autonomous. 23 stages. Zero hallucinated citations.</strong>
</p>

<p align="center">
  <a href="https://github.com/Randy-sin/ScholarClaw/stargazers"><img src="https://img.shields.io/github/stars/Randy-sin/ScholarClaw?style=social" alt="GitHub Stars"></a>&nbsp;
  <a href="https://github.com/Randy-sin/ScholarClaw/network/members"><img src="https://img.shields.io/github/forks/Randy-sin/ScholarClaw?style=social" alt="Forks"></a>&nbsp;
  <a href="https://github.com/Randy-sin/ScholarClaw/issues"><img src="https://img.shields.io/github/issues/Randy-sin/ScholarClaw?color=orange" alt="Issues"></a>&nbsp;
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>&nbsp;
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white" alt="Python 3.11+"></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-key-capabilities">Capabilities</a> •
  <a href="#%EF%B8%8F-configuration">Configuration</a> •
  <a href="docs/README_CN.md">中文文档</a>
</p>

---

> **ScholarClaw** takes a single research topic and autonomously produces a conference-grade academic paper — complete with real literature from arXiv, Semantic Scholar & OpenAlex, hardware-aware sandbox experiments, multi-agent peer review, and compile-ready LaTeX for NeurIPS / ICML / ICLR.

---

## ✨ Highlights

<table>
<tr>
<td width="50%">

**🔬 Real Research, Not Summaries**

Queries live academic APIs (arXiv, Semantic Scholar, OpenAlex), runs actual experiments in sandboxed environments, and verifies every citation through a 4-layer pipeline.

</td>
<td width="50%">

**🧠 Self-Healing & Self-Steering**

Experiments that crash get auto-diagnosed and repaired. Hypotheses that fail trigger an autonomous PIVOT to a new research direction — no human needed.

</td>
</tr>
<tr>
<td width="50%">

**📝 Conference-Ready Output**

Generates 5,000–6,500 word papers with proper LaTeX targeting NeurIPS, ICML, or ICLR. Upload `deliverables/` to Overleaf and compile directly.

</td>
<td width="50%">

**🛡️ Zero Hallucinated References**

4-layer citation verification: arXiv ID check → CrossRef/DataCite DOI → Semantic Scholar fuzzy match → LLM relevance scoring. Fake refs get killed.

</td>
</tr>
</table>

---

## 📦 What You Get

```
scholarclaw run --topic "Efficient attention for long-sequence time-series transformers"
```

```
artifacts/sc-20260318-143022-a7f3/
├── deliverables/
│   ├── paper.tex              # Conference-ready LaTeX
│   ├── references.bib         # Verified BibTeX (zero hallucinations)
│   ├── neurips_2025.sty       # Template style file
│   └── figures/               # Auto-generated plots
├── paper_draft.md             # Full paper in Markdown (8 sections)
├── experiments/
│   ├── run_001/               # Code + stdout + metrics.json
│   ├── run_002/               # Self-healed retry
│   └── comparison_charts/     # Error bars, confidence intervals
├── peer_review.md             # Multi-agent review (methodology + clarity)
├── verification_report.json   # 4-layer citation integrity audit
└── evolution/                 # Lessons learned for future runs
```

---

## 🚀 Quick Start

```bash
# 1️⃣  Clone
git clone https://github.com/Randy-sin/ScholarClaw.git
cd ScholarClaw

# 2️⃣  Install
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# 3️⃣  Configure
cp config.scholarclaw.example.yaml config.scholarclaw.yaml
# → Edit config.scholarclaw.yaml: set your LLM API key

# 4️⃣  Run
export OPENAI_API_KEY="sk-..."
scholarclaw run --topic "Your research idea" --auto-approve
```

<details>
<summary><b>📋 Minimal config.scholarclaw.yaml</b></summary>

```yaml
project:
  name: "my-research"

research:
  topic: "Your research topic"

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

## 🔬 How It Works

**23 stages across 8 phases.** Gate stages pause for human approval (or skip with `--auto-approve`).

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Phase A ─ Research Scoping         Phase E ─ Experiment Execution  │
│    1  TOPIC_INIT                      12  EXPERIMENT_RUN            │
│    2  PROBLEM_DECOMPOSE               13  ITERATIVE_REFINE  ← heal │
│                                                                     │
│  Phase B ─ Literature Discovery     Phase F ─ Analysis & Decision   │
│    3  SEARCH_STRATEGY                 14  RESULT_ANALYSIS   ← multi │
│    4  LITERATURE_COLLECT  ← API       15  RESEARCH_DECISION ← pivot │
│    5  LITERATURE_SCREEN   [gate]                                    │
│    6  KNOWLEDGE_EXTRACT             Phase G ─ Paper Writing         │
│                                       16  PAPER_OUTLINE             │
│  Phase C ─ Knowledge Synthesis        17  PAPER_DRAFT               │
│    7  SYNTHESIS                       18  PEER_REVIEW      ← check │
│    8  HYPOTHESIS_GEN      ← debate   19  PAPER_REVISION            │
│                                                                     │
│  Phase D ─ Experiment Design        Phase H ─ Finalization          │
│    9  EXPERIMENT_DESIGN   [gate]      20  QUALITY_GATE     [gate]  │
│   10  CODE_GENERATION                 21  KNOWLEDGE_ARCHIVE         │
│   11  RESOURCE_PLANNING               22  EXPORT_PUBLISH   ← LaTeX │
│                                       23  CITATION_VERIFY  ← 4-lyr │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

> **Decision loops:** Stage 15 evaluates results and autonomously decides **PROCEED**, **REFINE** (→ Stage 13), or **PIVOT** (→ Stage 8). All previous artifacts are versioned.

---

## 🎯 Key Capabilities

### 📚 Real Literature from Live APIs

| Source | What It Provides | Rate Limit |
|--------|-----------------|------------|
| **arXiv API** | Full-text search, PDF links, metadata | Unlimited |
| **Semantic Scholar** | Titles, DOIs, citation counts, abstracts | 100 req/5min (free) |
| **OpenAlex** | Broad coverage, institution data | Generous |

Auto-deduplication via DOI → arXiv ID → fuzzy title matching. Circuit breaker with graceful degradation when APIs are down.

### 🔍 4-Layer Citation Verification

Every reference in the final paper passes through:

| Layer | Method | Catches |
|-------|--------|---------|
| **L1** | arXiv API lookup | Fake arXiv IDs |
| **L2** | CrossRef + DataCite | Invalid DOIs, title mismatches |
| **L3** | Semantic Scholar | Non-existent papers (fuzzy match ≥0.80) |
| **L4** | LLM relevance scoring | Real but irrelevant padding citations |

Failed citations are removed. Uncited references are pruned from `.bib`.

### 🖥️ Hardware-Aware Experiments

Auto-detects compute tier and adapts generated code:

| Tier | Detection | Generated Code |
|------|-----------|---------------|
| **High** | NVIDIA GPU ≥8 GB | Full PyTorch + CUDA |
| **Limited** | NVIDIA <8 GB / Apple MPS | Lightweight models, smaller batches |
| **CPU-only** | No GPU | NumPy + scikit-learn only |

### 🔧 Self-Healing Execution

```
Code runs → fails?
  ├─ Read traceback
  ├─ LLM diagnoses root cause
  ├─ Generate targeted patch
  ├─ Re-run (up to 3 rounds)
  └─ Capture partial results on timeout
```

Sandbox features: AST validation, import whitelisting, NaN/Inf detection, memory limits.

### 🤖 Multi-Agent Peer Review

| Reviewer | Focus |
|----------|-------|
| **Methodology Agent** | Experiment sufficiency, confounds, reproducibility, statistical validity |
| **Clarity Agent** | Argument flow, term definitions, figure descriptions, readability |

Plus an **evidence-claim consistency check**: if the paper claims N experiments but only M ran, it gets flagged.

### 🔄 PIVOT / REFINE Decision Loop

Stage 15 evaluates experimental results against hypotheses:

| Decision | Trigger | Action |
|----------|---------|--------|
| **PROCEED** | Results support hypothesis | Continue to paper writing |
| **REFINE** | Promising but noisy | Tweak params → re-run experiments |
| **PIVOT** | Hypothesis unsupported | Generate new hypotheses → restart |

Each cycle auto-versions all artifacts for full traceability.

---

## 📐 Conference Templates

| Conference | Config Value | Layout |
|-----------|-------------|--------|
| NeurIPS 2025 | `neurips_2025` | Single column |
| ICLR 2026 | `iclr_2026` | Single column |
| ICML 2026 | `icml_2026` | Double column |

```yaml
export:
  target_conference: "neurips_2025"
```

The `deliverables/` folder includes `.sty`, `.bst`, and `.cls` files — upload to Overleaf and compile without extra setup.

---

## ⚙️ Configuration

<details>
<summary><b>Full config reference (click to expand)</b></summary>

```yaml
# ─── Project ───
project:
  name: "my-research"
  mode: "full-auto"                  # docs-first | semi-auto | full-auto

# ─── Research ───
research:
  topic: "..."
  domains: ["ml", "nlp"]
  daily_paper_count: 8
  quality_threshold: 4.0

# ─── LLM ───
llm:
  provider: "openai-compatible"      # or "acp"
  base_url: "https://api.openai.com/v1"
  api_key_env: "OPENAI_API_KEY"
  primary_model: "gpt-4o"
  fallback_models: ["gpt-4o-mini"]
  acp:
    agent: "claude"                  # claude | codex | gemini | kimi
    cwd: "."

# ─── Experiment ───
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

# ─── Export ───
export:
  target_conference: "neurips_2025"
  authors: "Anonymous"

# ─── Quality Gates ───
security:
  hitl_required_stages: [5, 9, 20]
  allow_publish_without_approval: false

# ─── Cross-Run Learning (Optional) ───
metaclaw_bridge:
  enabled: false
  skills_dir: "~/.metaclaw/skills"
```

</details>

---

## 🛠️ CLI Reference

```bash
# Full pipeline
scholarclaw run --topic "..." --auto-approve

# Custom config
scholarclaw run --config config.scholarclaw.yaml --topic "..."

# Resume from a stage
scholarclaw run --from-stage PAPER_OUTLINE --auto-approve

# Validate config
scholarclaw validate --config config.scholarclaw.yaml
```

---

## 🗂️ Project Structure

```
scholarclaw_engine/
├── pipeline/           # Stage runner, executor, contracts
├── literature/         # arXiv, Semantic Scholar, OpenAlex clients
├── experiment/         # Sandbox, Docker, SSH, self-healing
├── agents/             # CodeAgent, BenchmarkAgent, FigureAgent
├── templates/styles/   # NeurIPS / ICML / ICLR LaTeX
├── llm/                # LLM adapters (OpenAI-compatible, ACP)
├── metaclaw_bridge/    # Cross-run learning (optional)
└── knowledge/          # Structured knowledge base

tests/                  # Test suite
docs/                   # EN + CN documentation
```

---

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

```bash
# Development setup
git clone https://github.com/Randy-sin/ScholarClaw.git
cd ScholarClaw
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

---

## 📄 License

[MIT](LICENSE) — use it however you want.

---

<p align="center">
  <sub>Built with 🦞 by the ScholarClaw contributors</sub>
</p>
