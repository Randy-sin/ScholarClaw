"""ScholarClaw pipeline state machine.

Defines the stage sequence, status transitions, gate logic, and rollback rules.
The pipeline uses 12 stages grouped into 5 phases.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Iterable


class Stage(IntEnum):
    """12-stage research pipeline."""

    # Phase 1: Discovery
    RESEARCH_SCOPING = 1
    SEARCH_COLLECT = 2
    LITERATURE_SCREEN = 3       # GATE
    KNOWLEDGE_EXTRACT = 4

    # Phase 2: Ideation
    HYPOTHESIS_SYNTHESIS = 5
    EXPERIMENT_DESIGN = 6       # GATE
    CODE_SETUP = 7

    # Phase 3: Experimentation
    EXPERIMENT_EXECUTE = 8
    ANALYSIS_DECISION = 9

    # Phase 4: Composition
    PAPER_WRITE = 10

    # Phase 5: Delivery
    QUALITY_CHECK = 11          # GATE
    EXPORT_VERIFY = 12


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    BLOCKED_APPROVAL = "blocked_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAUSED = "paused"
    RETRYING = "retrying"
    FAILED = "failed"
    DONE = "done"


class TransitionEvent(str, Enum):
    START = "start"
    SUCCEED = "succeed"
    APPROVE = "approve"
    REJECT = "reject"
    TIMEOUT = "timeout"
    FAIL = "fail"
    RETRY = "retry"
    RESUME = "resume"
    PAUSE = "pause"


# ---------------------------------------------------------------------------
# Stage navigation
# ---------------------------------------------------------------------------

STAGE_SEQUENCE: tuple[Stage, ...] = tuple(Stage)

NEXT_STAGE: dict[Stage, Stage | None] = {
    stage: STAGE_SEQUENCE[idx + 1] if idx + 1 < len(STAGE_SEQUENCE) else None
    for idx, stage in enumerate(STAGE_SEQUENCE)
}

PREVIOUS_STAGE: dict[Stage, Stage | None] = {
    stage: STAGE_SEQUENCE[idx - 1] if idx > 0 else None
    for idx, stage in enumerate(STAGE_SEQUENCE)
}

# ---------------------------------------------------------------------------
# Gate stages — require approval before proceeding
# ---------------------------------------------------------------------------

GATE_STAGES: frozenset[Stage] = frozenset(
    {
        Stage.LITERATURE_SCREEN,
        Stage.EXPERIMENT_DESIGN,
        Stage.QUALITY_CHECK,
    }
)

GATE_ROLLBACK: dict[Stage, Stage] = {
    Stage.LITERATURE_SCREEN: Stage.SEARCH_COLLECT,
    Stage.EXPERIMENT_DESIGN: Stage.HYPOTHESIS_SYNTHESIS,
    Stage.QUALITY_CHECK: Stage.PAPER_WRITE,
}

# ---------------------------------------------------------------------------
# Research decision rollback targets (PIVOT/REFINE from Stage 9)
# ---------------------------------------------------------------------------

DECISION_ROLLBACK: dict[str, Stage] = {
    "pivot": Stage.HYPOTHESIS_SYNTHESIS,
    "refine": Stage.EXPERIMENT_EXECUTE,
}

MAX_DECISION_PIVOTS: int = 2

# ---------------------------------------------------------------------------
# Noncritical stages
# ---------------------------------------------------------------------------

NONCRITICAL_STAGES: frozenset[Stage] = frozenset()

# ---------------------------------------------------------------------------
# Phase groupings (for UI and reporting)
# ---------------------------------------------------------------------------

PHASE_MAP: dict[str, tuple[Stage, ...]] = {
    "Discovery": (
        Stage.RESEARCH_SCOPING,
        Stage.SEARCH_COLLECT,
        Stage.LITERATURE_SCREEN,
        Stage.KNOWLEDGE_EXTRACT,
    ),
    "Ideation": (
        Stage.HYPOTHESIS_SYNTHESIS,
        Stage.EXPERIMENT_DESIGN,
        Stage.CODE_SETUP,
    ),
    "Experimentation": (Stage.EXPERIMENT_EXECUTE, Stage.ANALYSIS_DECISION),
    "Composition": (Stage.PAPER_WRITE,),
    "Delivery": (Stage.QUALITY_CHECK, Stage.EXPORT_VERIFY),
}


# ---------------------------------------------------------------------------
# Transition logic
# ---------------------------------------------------------------------------

TRANSITION_MAP: dict[StageStatus, frozenset[StageStatus]] = {
    StageStatus.PENDING: frozenset({StageStatus.RUNNING}),
    StageStatus.RUNNING: frozenset(
        {StageStatus.DONE, StageStatus.BLOCKED_APPROVAL, StageStatus.FAILED}
    ),
    StageStatus.BLOCKED_APPROVAL: frozenset(
        {StageStatus.APPROVED, StageStatus.REJECTED, StageStatus.PAUSED}
    ),
    StageStatus.APPROVED: frozenset({StageStatus.DONE}),
    StageStatus.REJECTED: frozenset({StageStatus.PENDING}),
    StageStatus.PAUSED: frozenset({StageStatus.RUNNING}),
    StageStatus.RETRYING: frozenset({StageStatus.RUNNING}),
    StageStatus.FAILED: frozenset({StageStatus.RETRYING, StageStatus.PAUSED}),
    StageStatus.DONE: frozenset(),
}


@dataclass(frozen=True)
class TransitionOutcome:
    stage: Stage
    status: StageStatus
    next_stage: Stage | None
    rollback_stage: Stage | None = None
    checkpoint_required: bool = False
    decision: str = "proceed"


def gate_required(
    stage: Stage,
    hitl_required_stages: Iterable[int] | None = None,
) -> bool:
    """Check whether a stage requires human-in-the-loop approval."""
    if stage not in GATE_STAGES:
        return False
    if hitl_required_stages is not None:
        return int(stage) in frozenset(hitl_required_stages)
    return True  # Default: all gate stages require approval


def default_rollback_stage(stage: Stage) -> Stage:
    """Return the configured rollback target, or the previous stage."""
    return GATE_ROLLBACK.get(stage) or PREVIOUS_STAGE.get(stage) or stage


def advance(
    stage: Stage,
    status: StageStatus,
    event: TransitionEvent | str,
    *,
    hitl_required_stages: Iterable[int] | None = None,
    rollback_stage: Stage | None = None,
) -> TransitionOutcome:
    """Compute the next state given current stage, status, and event.

    Raises ValueError on unsupported transitions.
    """
    event = TransitionEvent(event)
    target_rollback = rollback_stage or default_rollback_stage(stage)

    # START → RUNNING
    if event is TransitionEvent.START and status in {
        StageStatus.PENDING,
        StageStatus.RETRYING,
        StageStatus.PAUSED,
    }:
        return TransitionOutcome(
            stage=stage, status=StageStatus.RUNNING, next_stage=stage
        )

    # SUCCEED while RUNNING
    if event is TransitionEvent.SUCCEED and status is StageStatus.RUNNING:
        if gate_required(stage, hitl_required_stages):
            return TransitionOutcome(
                stage=stage,
                status=StageStatus.BLOCKED_APPROVAL,
                next_stage=stage,
                checkpoint_required=False,
                decision="block",
            )
        return TransitionOutcome(
            stage=stage,
            status=StageStatus.DONE,
            next_stage=NEXT_STAGE[stage],
            checkpoint_required=True,
        )

    # APPROVE while BLOCKED
    if event is TransitionEvent.APPROVE and status is StageStatus.BLOCKED_APPROVAL:
        return TransitionOutcome(
            stage=stage,
            status=StageStatus.DONE,
            next_stage=NEXT_STAGE[stage],
            checkpoint_required=True,
        )

    # REJECT while BLOCKED → rollback
    if event is TransitionEvent.REJECT and status is StageStatus.BLOCKED_APPROVAL:
        return TransitionOutcome(
            stage=target_rollback,
            status=StageStatus.PENDING,
            next_stage=target_rollback,
            rollback_stage=target_rollback,
            checkpoint_required=True,
            decision="pivot",
        )

    # TIMEOUT while BLOCKED → pause
    if event is TransitionEvent.TIMEOUT and status is StageStatus.BLOCKED_APPROVAL:
        return TransitionOutcome(
            stage=stage,
            status=StageStatus.PAUSED,
            next_stage=stage,
            checkpoint_required=True,
            decision="block",
        )

    # FAIL while RUNNING
    if event is TransitionEvent.FAIL and status is StageStatus.RUNNING:
        return TransitionOutcome(
            stage=stage,
            status=StageStatus.FAILED,
            next_stage=stage,
            checkpoint_required=True,
            decision="retry",
        )

    # RETRY while FAILED
    if event is TransitionEvent.RETRY and status is StageStatus.FAILED:
        return TransitionOutcome(
            stage=stage,
            status=StageStatus.RETRYING,
            next_stage=stage,
            decision="retry",
        )

    # RESUME while PAUSED
    if event is TransitionEvent.RESUME and status is StageStatus.PAUSED:
        return TransitionOutcome(
            stage=stage, status=StageStatus.RUNNING, next_stage=stage
        )

    # PAUSE while FAILED
    if event is TransitionEvent.PAUSE and status is StageStatus.FAILED:
        return TransitionOutcome(
            stage=stage,
            status=StageStatus.PAUSED,
            next_stage=stage,
            checkpoint_required=True,
            decision="block",
        )

    raise ValueError(
        f"Unsupported transition: {status.value} + {event.value} for stage {int(stage)}"
    )
