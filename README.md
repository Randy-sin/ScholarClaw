<p align="center">
  <img src="image/banner.png" width="680" alt="ScholarClaw">
</p>

<p align="center">
  <a href="https://github.com/Randy-sin/ScholarClaw/stargazers"><img src="https://img.shields.io/github/stars/Randy-sin/ScholarClaw?style=social" alt="Stars"></a>&nbsp;
  <a href="https://github.com/Randy-sin/ScholarClaw/network/members"><img src="https://img.shields.io/github/forks/Randy-sin/ScholarClaw?style=social" alt="Forks"></a>&nbsp;
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT"></a>&nbsp;
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" alt="Python"></a>
</p>

<p align="center">
  <a href="#get-started">Get Started</a> &middot;
  <a href="#under-the-hood">Under the Hood</a> &middot;
  <a href="#trust-but-verify">Trust but Verify</a> &middot;
  <a href="docs/README_CN.md">📖 中文文档 / Chinese Docs</a>
</p>

---

ScholarClaw is an end-to-end research automation engine.
You describe a research direction in plain text; it comes back with a draft paper, real references, executed experiments, and LaTeX you can compile on Overleaf.

**The problem it solves:** writing an academic paper involves dozens of tedious, error-prone steps — searching literature, designing experiments, running code, formatting citations, typesetting LaTeX. ScholarClaw chains these steps into a single deterministic pipeline so you can focus on the ideas instead of the plumbing.

---

## Get Started

```bash
git clone https://github.com/Randy-sin/ScholarClaw.git && cd ScholarClaw
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp config.scholarclaw.example.yaml config.scholarclaw.yaml   # edit: add your API key
scholarclaw run --topic "your research question" --auto-approve
```

Results land in `artifacts/`. The `deliverables/` subfolder is Overleaf-ready.

<details>
<summary>Minimal YAML config</summary>

```yaml
project:
  name: "my-project"
research:
  topic: "your topic"
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

## What Comes Out

A single run produces a self-contained research artifact:

| File | What it is |
|------|-----------|
| `paper_draft.md` | 5 000 – 6 500 word draft covering introduction through conclusion |
| `paper.tex` + `*.sty` | Compile-ready LaTeX (NeurIPS / ICML / ICLR) |
| `paper.pdf` | Auto-compiled PDF *(requires `pdflatex` — see note below)* |
| `references.bib` | BibTeX entries — each one verified against live databases |
| `experiments/` | Generated Python code, stdout logs, `metrics.json` per run |
| `charts/` | Comparison plots with error bars |
| `peer_review.md` | Automated critique (methodology + clarity) |
| `verification_report.json` | Per-reference audit trail |

> **PDF generation note:** If `pdflatex` is installed on your system, the pipeline automatically compiles `paper.tex` into `paper.pdf` (with up to 3 auto-repair attempts for common LaTeX errors). If `pdflatex` is not available, the pipeline completes normally and outputs `.tex` + `.bib` files — you can compile them on [Overleaf](https://overleaf.com) or with any local TeX distribution (`brew install --cask mactex` on macOS, `sudo apt install texlive-full` on Ubuntu, or [tectonic](https://tectonic-typesetting.github.io/) as a lightweight alternative).

---

## Under the Hood

The pipeline is split into **five phases**, each responsible for one concern:

```
 Discovery       → scope the problem, search literature, screen, extract knowledge
 Ideation        → synthesize findings, form hypotheses, design experiments, generate code
 Experimentation → run in sandbox, auto-repair, analyze results, decide: continue or pivot
 Composition     → draft the paper, run peer review, revise
 Delivery        → quality check, LaTeX export, citation audit
```

Two feedback loops keep the pipeline from going off the rails:

- **Adjust** — results are promising but noisy → tweak parameters, re-run.
- **Pivot** — hypothesis is dead → generate a new one, restart from synthesis.

Every loop iteration snapshots all artifacts so nothing is lost.

---

## Trust but Verify

The biggest risk with LLM-generated papers is fake citations. ScholarClaw addresses this with a multi-pass verification system after the draft is complete:

| Pass | Source | What it catches |
|------|--------|----------------|
| 1 | arXiv API | Non-existent arXiv identifiers |
| 2 | CrossRef / DataCite | DOIs that don't resolve or whose titles don't match |
| 3 | Semantic Scholar | Papers that simply don't exist (fuzzy title match ≥ 0.80) |
| 4 | LLM re-scoring | Real papers that have nothing to do with the topic |

References that fail any pass are removed from the `.bib` and the in-text `\cite{}` calls. The audit trail is saved to `verification_report.json`.

---

## Hardware Adaptation

Before generating experiment code, ScholarClaw probes the local environment:

| Detected | Strategy |
|----------|----------|
| NVIDIA GPU ≥ 8 GB | Full PyTorch + CUDA |
| NVIDIA < 8 GB or Apple MPS | Lighter models, smaller batches |
| CPU only | NumPy / scikit-learn workloads |

This means the same topic produces runnable code on a MacBook Air and on a multi-GPU server — the pipeline adjusts automatically.

---

## Experiment Sandbox

Generated code runs inside a restricted sandbox:

- **AST pre-check** — rejects code with disallowed imports before execution.
- **Divergence guard** — kills runs that produce NaN / Inf early.
- **Auto-repair** — on failure, the traceback is fed back to the LLM, which produces a targeted patch. Up to 3 repair rounds.
- **Partial capture** — if a run times out, whatever metrics were collected are still saved.

---

## Automated Review

After the draft is written, two review passes run automatically:

1. **Methodology pass** — checks whether the experiments actually support the claims, flags missing baselines, notes reproducibility gaps.
2. **Clarity pass** — checks argument flow, undefined terms, figure/table descriptions.

An additional consistency check compares the number of experiments described in the paper against the number that actually ran.

---

## LaTeX Templates

| Target | Config value | Notes |
|--------|-------------|-------|
| NeurIPS 2025 | `neurips_2025` | Single-column |
| ICLR 2026 | `iclr_2026` | Single-column |
| ICML 2026 | `icml_2026` | Double-column |

```yaml
export:
  target_conference: "neurips_2025"
```

Style files (`.sty`, `.bst`, `.cls`) are bundled in `deliverables/` — upload the folder to Overleaf and compile.

---

## Configuration

<details>
<summary>Full reference</summary>

```yaml
project:
  name: "my-research"
  mode: "full-auto"              # docs-first | semi-auto | full-auto

research:
  topic: "..."
  domains: ["ml", "nlp"]

llm:
  provider: "openai-compatible"  # or "acp"
  base_url: "https://api.openai.com/v1"
  api_key_env: "OPENAI_API_KEY"
  primary_model: "gpt-4o"
  fallback_models: ["gpt-4o-mini"]
  acp:                           # when provider is "acp"
    agent: "claude"              # any ACP-compatible CLI
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
  hitl_required_stages: [3, 6, 11]   # gate stages
  allow_publish_without_approval: false
```
</details>

---

## CLI

```bash
scholarclaw run --topic "..." --auto-approve          # full pipeline
scholarclaw run --config my.yaml --topic "..."        # custom config
scholarclaw run --from-stage PAPER_WRITE               # resume mid-pipeline
scholarclaw validate --config my.yaml                  # dry-run config check
```

---

## Project Layout

```
scholarclaw_engine/
  pipeline/         stage runner + executor
  literature/       arXiv, Semantic Scholar, OpenAlex clients
  experiment/       sandbox, Docker, SSH, auto-repair
  agents/           CodeAgent, BenchmarkAgent, FigureAgent
  templates/        NeurIPS / ICML / ICLR LaTeX styles
  llm/              LLM adapters
  knowledge/        structured knowledge base
tests/
docs/               EN + CN
```

---

## Contributing

PRs welcome — please open an issue first so we can discuss scope.

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

---

## License

MIT — see [LICENSE](LICENSE).

<p align="center"><sub>🦞</sub></p>
