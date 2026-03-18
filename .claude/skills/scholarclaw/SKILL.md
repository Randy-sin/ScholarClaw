# ScholarClaw — Autonomous Research Pipeline Skill

## Description

Run ScholarClaw's autonomous research pipeline. Given a research topic, this skill orchestrates the entire research workflow: literature discovery → hypothesis synthesis → experiment execution → paper writing → export with citation verification.

## Trigger Conditions

Activate this skill when the user:
- Asks to "research [topic]", "write a paper about [topic]", or "investigate [topic]"
- Wants to run an autonomous research pipeline
- Asks to generate a research paper from scratch
- Mentions "ScholarClaw" by name

## Instructions

### Prerequisites Check

1. Verify config file exists:
   ```bash
   ls config.yaml || ls config.scholarclaw.example.yaml
   ```
2. If no `config.yaml`, create one from the example:
   ```bash
   cp config.scholarclaw.example.yaml config.yaml
   ```
3. Ensure the user's LLM API key is configured in `config.yaml` under `llm.api_key` or via `llm.api_key_env` environment variable.

### Running the Pipeline

**Option A: CLI (recommended)**

```bash
scholarclaw run --topic "Your research topic here" --auto-approve
```

Options:
- `--topic` / `-t`: Override the research topic from config
- `--config` / `-c`: Config file path (default: `config.yaml`)
- `--output` / `-o`: Output directory (default: `artifacts/rc-YYYYMMDD-HHMMSS-HASH/`)
- `--from-stage`: Resume from a specific stage (e.g., `PAPER_WRITE`)
- `--auto-approve`: Auto-approve gate stages (3, 6, 11) without human input

**Option B: Python API**

```python
from scholarclaw_engine.pipeline.runner import execute_pipeline
from scholarclaw_engine.config import RCConfig
from scholarclaw_engine.adapters import AdapterBundle
from pathlib import Path

config = RCConfig.load("config.yaml", check_paths=False)
results = execute_pipeline(
    run_dir=Path("artifacts/my-run"),
    run_id="research-001",
    config=config,
    adapters=AdapterBundle(),
    auto_approve_gates=True,
)

# Check results
for r in results:
    print(f"Stage {r.stage.name}: {r.status.value}")
```

**Option C: Iterative Pipeline (multi-round improvement)**

```python
from scholarclaw_engine.pipeline.runner import execute_iterative_pipeline

results = execute_iterative_pipeline(
    run_dir=Path("artifacts/my-run"),
    run_id="research-001",
    config=config,
    adapters=AdapterBundle(),
    max_iterations=3,
    convergence_rounds=2,
)
```

### Output Structure

After a successful run, the output directory contains:

```
artifacts/<run-id>/
├── stage-01/               # RESEARCH_SCOPING outputs
├── stage-02/               # SEARCH_COLLECT outputs
├── ...
├── stage-07/
│   └── experiment/         # Generated experiment code
├── stage-08/
│   └── runs/run-1.json     # Experiment execution results
├── stage-09/
│   ├── analysis.md         # Results analysis
│   └── decision.md         # PROCEED/PIVOT decision
├── stage-10/
│   └── paper_draft.md      # Full paper draft
├── stage-12/
│   └── verification_report.json  # Citation audit
└── pipeline_summary.json   # Overall pipeline status
```

### Experiment Modes

| Mode | Description | Config |
|------|-------------|--------|
| `simulated` | LLM generates synthetic results (no code execution) | `experiment.mode: simulated` |
| `sandbox` | Execute generated code locally via subprocess | `experiment.mode: sandbox` |
| `ssh_remote` | Execute on remote GPU server via SSH | `experiment.mode: ssh_remote` |

### Troubleshooting

- **Config validation error**: Run `scholarclaw validate --config config.yaml`
- **LLM connection failure**: Check `llm.base_url` and API key
- **Sandbox execution failure**: Verify `experiment.sandbox.python_path` exists and has numpy installed
- **Gate rejection**: Use `--auto-approve` or manually approve at stages 3, 6, 11

## Tools Required

- File read/write (for config and artifacts)
- Bash (for CLI execution)
- No external MCP servers required for basic operation
