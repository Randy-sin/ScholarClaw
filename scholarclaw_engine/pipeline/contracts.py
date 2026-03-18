"""Stage I/O contracts for the ScholarClaw pipeline.

Each StageContract declares:
  - input_files: artifacts this stage reads (produced by prior stages)
  - output_files: artifacts this stage must produce
  - dod: Definition of Done — human-readable acceptance criterion
  - error_code: unique error identifier for diagnostics
  - max_retries: how many times the stage may be retried on failure
"""

from __future__ import annotations

from dataclasses import dataclass

from scholarclaw_engine.pipeline.stages import Stage


@dataclass(frozen=True)
class StageContract:
    stage: Stage
    input_files: tuple[str, ...]
    output_files: tuple[str, ...]
    dod: str
    error_code: str
    max_retries: int = 1


CONTRACTS: dict[Stage, StageContract] = {
    # Phase 1: Discovery
    Stage.RESEARCH_SCOPING: StageContract(
        stage=Stage.RESEARCH_SCOPING,
        input_files=(),
        output_files=("goal.md", "hardware_profile.json", "problem_tree.md"),
        dod="SMART goal + >=3 prioritized sub-questions + hardware profile",
        error_code="E01_SCOPING_FAIL",
        max_retries=0,
    ),
    Stage.SEARCH_COLLECT: StageContract(
        stage=Stage.SEARCH_COLLECT,
        input_files=("problem_tree.md",),
        output_files=("search_plan.yaml", "sources.json", "queries.json", "candidates.jsonl"),
        dod="Search strategies defined and candidate papers collected",
        error_code="E02_SEARCH_FAIL",
        max_retries=2,
    ),
    Stage.LITERATURE_SCREEN: StageContract(
        stage=Stage.LITERATURE_SCREEN,
        input_files=("candidates.jsonl",),
        output_files=("shortlist.jsonl",),
        dod="Relevance + quality dual screening completed and approved",
        error_code="E03_GATE_REJECT",
        max_retries=0,
    ),
    Stage.KNOWLEDGE_EXTRACT: StageContract(
        stage=Stage.KNOWLEDGE_EXTRACT,
        input_files=("shortlist.jsonl",),
        output_files=("cards/",),
        dod="Structured knowledge card per shortlisted paper",
        error_code="E04_EXTRACT_FAIL",
    ),
    # Phase 2: Ideation
    Stage.HYPOTHESIS_SYNTHESIS: StageContract(
        stage=Stage.HYPOTHESIS_SYNTHESIS,
        input_files=("cards/",),
        output_files=("synthesis.md", "hypotheses.md"),
        dod="Topic clusters, research gaps, and >=2 falsifiable hypotheses",
        error_code="E05_HYPOTHESIS_FAIL",
    ),
    Stage.EXPERIMENT_DESIGN: StageContract(
        stage=Stage.EXPERIMENT_DESIGN,
        input_files=("hypotheses.md",),
        output_files=("exp_plan.yaml",),
        dod="Experiment plan with baselines, ablations, metrics approved",
        error_code="E06_GATE_REJECT",
        max_retries=0,
    ),
    Stage.CODE_SETUP: StageContract(
        stage=Stage.CODE_SETUP,
        input_files=("exp_plan.yaml",),
        output_files=("experiment/", "experiment_spec.md", "schedule.json"),
        dod="Experiment code generated + resource schedule ready",
        error_code="E07_SETUP_FAIL",
        max_retries=2,
    ),
    # Phase 3: Experimentation
    Stage.EXPERIMENT_EXECUTE: StageContract(
        stage=Stage.EXPERIMENT_EXECUTE,
        input_files=("schedule.json", "experiment/"),
        output_files=("runs/", "refinement_log.json", "experiment_final/"),
        dod="All experiments executed with iterative refinement converged",
        error_code="E08_EXEC_FAIL",
        max_retries=2,
    ),
    Stage.ANALYSIS_DECISION: StageContract(
        stage=Stage.ANALYSIS_DECISION,
        input_files=("runs/",),
        output_files=("analysis.md", "decision.md"),
        dod="Results analyzed + PROCEED/PIVOT decision with justification",
        error_code="E09_ANALYSIS_FAIL",
    ),
    # Phase 4: Composition
    Stage.PAPER_WRITE: StageContract(
        stage=Stage.PAPER_WRITE,
        input_files=("analysis.md", "decision.md"),
        output_files=("paper_draft.md", "reviews.md", "paper_revised.md"),
        dod="Full paper drafted, peer-reviewed, and revised",
        error_code="E10_WRITE_FAIL",
        max_retries=2,
    ),
    # Phase 5: Delivery
    Stage.QUALITY_CHECK: StageContract(
        stage=Stage.QUALITY_CHECK,
        input_files=("paper_revised.md",),
        output_files=("quality_report.json",),
        dod="Quality score meets threshold and approved",
        error_code="E11_GATE_REJECT",
        max_retries=0,
    ),
    Stage.EXPORT_VERIFY: StageContract(
        stage=Stage.EXPORT_VERIFY,
        input_files=("paper_revised.md",),
        output_files=("paper_final.md", "code/", "verification_report.json", "references_verified.bib"),
        dod="LaTeX exported, citations verified, archive bundled",
        error_code="E12_EXPORT_FAIL",
    ),
}
