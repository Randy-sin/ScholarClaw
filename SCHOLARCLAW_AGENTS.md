# ScholarClaw — Agent Instructions

You are a **Research Orchestrator**. Your job is to help the user run ScholarClaw's autonomous research pipeline. When the user asks you to research a topic, write a paper, or investigate something, follow the steps below.

## Quick Start

```bash
# 1. Install
pip install -e .

# 2. Configure
cp config.scholarclaw.example.yaml config.yaml
# Edit config.yaml: set llm.api_key_env or llm.api_key, and research.topic

# 3. Run
scholarclaw run --topic "Your research topic" --auto-approve
```

## What You Do

1. **Check prerequisites**: Python 3.11+, config file, LLM API key
2. **Clone & install** (if not already done): `git clone` → `pip install -e .`
3. **Create config**: Copy `config.scholarclaw.example.yaml` → `config.yaml`, fill in the user's API key and topic
4. **Run the pipeline**: `scholarclaw run --topic "..." --auto-approve`
5. **Return results**: Point the user to the `deliverables/` folder

## Pipeline Overview

ScholarClaw runs 12 stages across 5 phases:

| Phase | Stages | What happens |
|-------|--------|-------------|
| Discovery | 1–3 | Scope the problem, search literature (arXiv + Semantic Scholar), screen papers |
| Ideation | 4–6 | Extract knowledge, synthesize hypotheses, design experiments |
| Experimentation | 7–9 | Generate code, run in sandbox, analyze results, decide: proceed/pivot/refine |
| Composition | 10–11 | Write the paper, peer review, revise, quality check |
| Delivery | 12 | Export LaTeX, verify all citations, archive knowledge |

Gate stages (3, 6, 11) can pause for human approval. Use `--auto-approve` to skip.

## Output

After a successful run, the `deliverables/` folder contains everything the user needs:

```
deliverables/
├── paper.tex               # Conference-ready LaTeX (NeurIPS / ICML / ICLR)
├── paper.pdf               # Auto-compiled PDF (if pdflatex is installed)
├── references.bib          # Verified BibTeX references
├── neurips_2025.sty        # Conference style file
├── code/                   # Experiment code + requirements.txt
├── charts/                 # Result visualizations
├── verification_report.json # Citation audit trail
└── manifest.json           # Deliverables manifest
```

> If `pdflatex` is not installed, the pipeline still completes — it outputs `.tex` + `.bib` that can be compiled on [Overleaf](https://overleaf.com).

## Configuration

Minimum required fields in `config.yaml`:

```yaml
research:
  topic: "Your research topic"

llm:
  base_url: "https://api.openai.com/v1"
  api_key_env: "OPENAI_API_KEY"       # or api_key: "sk-..."
  primary_model: "gpt-4o"

experiment:
  mode: "sandbox"                      # simulated | sandbox | docker | ssh_remote
  sandbox:
    python_path: ".venv/bin/python"
```

## CLI Reference

```bash
# Full pipeline
scholarclaw run --topic "..." --auto-approve

# Validate config only
scholarclaw validate --config config.yaml

# Resume from a specific stage
scholarclaw run --from-stage PAPER_WRITE --auto-approve

# Custom config path
scholarclaw run --config my-config.yaml --auto-approve
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Config validation error | `scholarclaw validate --config config.yaml` |
| LLM connection failure | Check `llm.base_url` and API key |
| Sandbox execution failure | Verify `experiment.sandbox.python_path` exists |
| Gate blocks pipeline | Use `--auto-approve` |
| Citations marked HALLUCINATED | Expected — Stage 12 catches these automatically |
