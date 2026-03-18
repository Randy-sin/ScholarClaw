#!/usr/bin/env python3
"""Real E2E test: run all 12 stages with actual LLM API calls.

Usage:
    .venv_arc/bin/python3 tests/e2e_real_llm.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import yaml

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scholarclaw_engine.config import RCConfig
from scholarclaw_engine.adapters import AdapterBundle
from scholarclaw_engine.llm.client import LLMClient
from scholarclaw_engine.pipeline.stages import Stage, STAGE_SEQUENCE
from scholarclaw_engine.pipeline.executor import execute_stage, StageResult
from scholarclaw_engine.pipeline.runner import execute_pipeline


def main() -> None:
    # --- Load config ---
    config_path = Path("config.scholarclaw.yaml")
    if not config_path.exists():
        print("ERROR: config.scholarclaw.yaml not found")
        sys.exit(1)

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    # Override for test
    raw["research"]["topic"] = (
        "Efficient Attention Mechanisms for Long-Context Language Models"
    )
    raw["experiment"]["mode"] = "sandbox"
    raw["experiment"]["time_budget_sec"] = 60
    raw["experiment"]["max_iterations"] = 3

    config = RCConfig.from_dict(raw, check_paths=False)
    adapters = AdapterBundle()

    # --- Create run directory ---
    run_dir = Path("artifacts/e2e-real-llm-run")
    run_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"e2e-real-{int(time.time())}"

    print(f"=" * 70)
    print(f"ScholarClaw E2E Test — Real LLM API")
    print(f"Topic: {config.research.topic}")
    print(f"Run ID: {run_id}")
    print(f"Output: {run_dir}")
    print(f"=" * 70)

    # --- Run full pipeline ---
    start = time.time()
    results = execute_pipeline(
        run_dir=run_dir,
        run_id=run_id,
        config=config,
        adapters=adapters,
        auto_approve_gates=True,  # Auto-approve all gates for E2E test
        kb_root=run_dir / "kb",
    )
    total_time = time.time() - start

    # --- Report ---
    print(f"\n{'=' * 70}")
    print(f"RESULTS: {len(results)}/12 stages executed in {total_time:.1f}s")
    print(f"{'=' * 70}")

    passed = 0
    failed = 0
    for r in results:
        status_icon = "✅" if r.status.value == "done" else "❌"
        print(
            f"  {status_icon} Stage {int(r.stage):02d} {r.stage.name}: {r.status.value} | artifacts: {r.artifacts}"
        )
        if r.status.value == "done":
            passed += 1
        else:
            failed += 1

    print(f"\n{'=' * 70}")
    print(f"SUMMARY: {passed} passed, {failed} failed, {total_time:.1f}s total")
    print(f"{'=' * 70}")

    # --- Validate key artifacts ---
    checks = [
        ("Stage 1 goal.md", "stage-01/goal.md"),
        ("Stage 7 experiment.py", "stage-07/experiment.py"),
        ("Stage 8 runs/", "stage-08/runs"),
        ("Stage 9 experiment_summary.json", "stage-09/experiment_summary.json"),
        ("Stage 10 paper_draft.md", "stage-10/paper_draft.md"),
        ("Stage 12 export files", "stage-12"),
    ]
    print("\nArtifact Checks:")
    for label, path in checks:
        full = run_dir / path
        exists = full.exists()
        if full.is_file():
            size = full.stat().st_size
            print(f"  {'✅' if exists else '❌'} {label}: {size} bytes")
        elif full.is_dir():
            count = len(list(full.iterdir())) if exists else 0
            print(f"  {'✅' if exists else '❌'} {label}: {count} items")
        else:
            print(f"  {'❌'} {label}: NOT FOUND")

    # --- Check experiment_summary.json has real data ---
    summary_path = run_dir / "stage-09" / "experiment_summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text())
        has_metrics = bool(summary.get("metrics_summary"))
        print(
            f"\n  📊 Experiment summary has real metrics: {'YES' if has_metrics else 'NO'}"
        )
        if has_metrics:
            for k, v in summary["metrics_summary"].items():
                print(f"     - {k}: {v}")

    # --- Check paper draft has real data (not placeholder) ---
    draft_path = run_dir / "stage-10" / "paper_draft.md"
    if draft_path.exists():
        draft = draft_path.read_text()
        has_placeholder = "no quantitative results yet" in draft.lower()
        has_template = draft.count("Template") > 3
        print(
            f"  📝 Paper draft: {len(draft)} chars, placeholder={has_placeholder}, template={has_template}"
        )

    # --- Check validation report ---
    val_report = run_dir / "stage-07" / "validation_report.md"
    if val_report.exists():
        print(f"  🔍 Code validation report: {val_report.stat().st_size} bytes")
        print(f"     {val_report.read_text()[:200]}")

    # Final verdict
    if passed == 12 and failed == 0:
        print(f"\n🎉 ALL 12 STAGES PASSED!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed} stages did not pass.")
        sys.exit(1)


if __name__ == "__main__":
    main()
