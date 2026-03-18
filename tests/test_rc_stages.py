import pytest

from scholarclaw_engine.pipeline.stages import (
    DECISION_ROLLBACK,
    GATE_ROLLBACK,
    GATE_STAGES,
    MAX_DECISION_PIVOTS,
    NEXT_STAGE,
    PHASE_MAP,
    PREVIOUS_STAGE,
    STAGE_SEQUENCE,
    TRANSITION_MAP,
    Stage,
    StageStatus,
    TransitionEvent,
    TransitionOutcome,
    advance,
    default_rollback_stage,
    gate_required,
)


def test_stage_enum_has_exactly_12_members():
    assert len(Stage) == 12


@pytest.mark.parametrize(
    "index,stage", [(idx, stage) for idx, stage in enumerate(STAGE_SEQUENCE, start=1)]
)
def test_stage_values_follow_sequence_order(index: int, stage: Stage):
    assert int(stage) == index


def test_stage_sequence_contains_all_12_stages_in_order():
    assert len(STAGE_SEQUENCE) == 12
    assert STAGE_SEQUENCE[0] is Stage.RESEARCH_SCOPING
    assert STAGE_SEQUENCE[-1] is Stage.EXPORT_VERIFY
    assert tuple(Stage) == STAGE_SEQUENCE


def test_next_stage_boundary_values():
    assert NEXT_STAGE[Stage.RESEARCH_SCOPING] is Stage.SEARCH_COLLECT
    assert NEXT_STAGE[Stage.QUALITY_CHECK] is Stage.EXPORT_VERIFY


def test_previous_stage_boundary_values():
    assert PREVIOUS_STAGE[Stage.RESEARCH_SCOPING] is None
    assert PREVIOUS_STAGE[Stage.SEARCH_COLLECT] is Stage.RESEARCH_SCOPING


def test_gate_stages_matches_expected_set():
    assert GATE_STAGES == frozenset(
        {Stage.LITERATURE_SCREEN, Stage.EXPERIMENT_DESIGN, Stage.QUALITY_CHECK}
    )


def test_gate_rollback_map_matches_expected_targets():
    assert GATE_ROLLBACK == {
        Stage.LITERATURE_SCREEN: Stage.SEARCH_COLLECT,
        Stage.EXPERIMENT_DESIGN: Stage.HYPOTHESIS_SYNTHESIS,
        Stage.QUALITY_CHECK: Stage.PAPER_WRITE,
    }


def test_phase_map_has_5_phases_with_expected_membership():
    assert len(PHASE_MAP) == 5
    assert PHASE_MAP["Discovery"] == (
        Stage.RESEARCH_SCOPING,
        Stage.SEARCH_COLLECT,
        Stage.LITERATURE_SCREEN,
        Stage.KNOWLEDGE_EXTRACT,
    )
    assert PHASE_MAP["Ideation"] == (
        Stage.HYPOTHESIS_SYNTHESIS,
        Stage.EXPERIMENT_DESIGN,
        Stage.CODE_SETUP,
    )
    assert PHASE_MAP["Experimentation"] == (
        Stage.EXPERIMENT_EXECUTE,
        Stage.ANALYSIS_DECISION,
    )
    assert PHASE_MAP["Composition"] == (Stage.PAPER_WRITE,)
    assert PHASE_MAP["Delivery"] == (Stage.QUALITY_CHECK, Stage.EXPORT_VERIFY)


def test_phase_map_covers_all_stages_exactly_once():
    flattened = tuple(stage for stages in PHASE_MAP.values() for stage in stages)
    assert len(flattened) == 12
    assert set(flattened) == set(Stage)


@pytest.mark.parametrize(
    "status",
    [StageStatus.PENDING, StageStatus.RETRYING, StageStatus.PAUSED],
)
def test_start_event_transitions_to_running_from_allowed_states(status: StageStatus):
    outcome = advance(Stage.EXPERIMENT_EXECUTE, status, TransitionEvent.START)

    assert outcome.status is StageStatus.RUNNING
    assert outcome.next_stage is Stage.EXPERIMENT_EXECUTE


def test_succeed_event_on_non_gate_stage_transitions_to_done():
    outcome = advance(
        Stage.SEARCH_COLLECT,
        StageStatus.RUNNING,
        TransitionEvent.SUCCEED,
        hitl_required_stages=(3, 6, 11),
    )

    assert outcome.status is StageStatus.DONE
    assert outcome.next_stage is Stage.LITERATURE_SCREEN
    assert outcome.checkpoint_required is True
    assert outcome.decision == "proceed"


def test_succeed_event_on_gate_stage_transitions_to_blocked_approval():
    outcome = advance(
        Stage.LITERATURE_SCREEN,
        StageStatus.RUNNING,
        TransitionEvent.SUCCEED,
        hitl_required_stages=(3, 11),
    )

    assert outcome.status is StageStatus.BLOCKED_APPROVAL
    assert outcome.next_stage is Stage.LITERATURE_SCREEN
    assert outcome.checkpoint_required is False
    assert outcome.decision == "block"


def test_approve_event_transitions_blocked_stage_to_done():
    outcome = advance(
        Stage.EXPERIMENT_DESIGN,
        StageStatus.BLOCKED_APPROVAL,
        TransitionEvent.APPROVE,
        hitl_required_stages=(3, 6, 11),
    )

    assert outcome.status is StageStatus.DONE
    assert outcome.next_stage is Stage.CODE_SETUP
    assert outcome.checkpoint_required is True


def test_reject_event_rolls_back_to_default_gate_mapping():
    outcome = advance(
        Stage.QUALITY_CHECK,
        StageStatus.BLOCKED_APPROVAL,
        TransitionEvent.REJECT,
        hitl_required_stages=(3, 6, 11),
    )

    assert outcome.status is StageStatus.PENDING
    assert outcome.stage is Stage.PAPER_WRITE
    assert outcome.next_stage is Stage.PAPER_WRITE
    assert outcome.rollback_stage is Stage.PAPER_WRITE
    assert outcome.checkpoint_required is True
    assert outcome.decision == "pivot"


def test_reject_event_uses_explicit_rollback_stage_when_provided():
    outcome = advance(
        Stage.PAPER_WRITE,
        StageStatus.BLOCKED_APPROVAL,
        TransitionEvent.REJECT,
        rollback_stage=Stage.PAPER_WRITE,
    )

    assert outcome.status is StageStatus.PENDING
    assert outcome.stage is Stage.PAPER_WRITE
    assert outcome.next_stage is Stage.PAPER_WRITE
    assert outcome.rollback_stage is Stage.PAPER_WRITE


def test_timeout_event_transitions_to_paused_with_block_decision():
    outcome = advance(
        Stage.LITERATURE_SCREEN,
        StageStatus.BLOCKED_APPROVAL,
        TransitionEvent.TIMEOUT,
    )

    assert outcome.status is StageStatus.PAUSED
    assert outcome.next_stage is Stage.LITERATURE_SCREEN
    assert outcome.checkpoint_required is True
    assert outcome.decision == "block"


def test_fail_event_transitions_running_to_failed_with_retry_decision():
    outcome = advance(Stage.EXPERIMENT_EXECUTE, StageStatus.RUNNING, TransitionEvent.FAIL)

    assert outcome.status is StageStatus.FAILED
    assert outcome.next_stage is Stage.EXPERIMENT_EXECUTE
    assert outcome.checkpoint_required is True
    assert outcome.decision == "retry"


def test_retry_event_transitions_failed_to_retrying():
    outcome = advance(Stage.EXPERIMENT_EXECUTE, StageStatus.FAILED, TransitionEvent.RETRY)

    assert outcome.status is StageStatus.RETRYING
    assert outcome.next_stage is Stage.EXPERIMENT_EXECUTE
    assert outcome.decision == "retry"


def test_resume_event_transitions_paused_to_running():
    outcome = advance(Stage.EXPERIMENT_EXECUTE, StageStatus.PAUSED, TransitionEvent.RESUME)

    assert outcome.status is StageStatus.RUNNING
    assert outcome.next_stage is Stage.EXPERIMENT_EXECUTE


def test_pause_event_transitions_failed_to_paused():
    outcome = advance(Stage.EXPERIMENT_EXECUTE, StageStatus.FAILED, TransitionEvent.PAUSE)

    assert outcome.status is StageStatus.PAUSED
    assert outcome.next_stage is Stage.EXPERIMENT_EXECUTE
    assert outcome.checkpoint_required is True
    assert outcome.decision == "block"


def test_invalid_transition_raises_value_error():
    with pytest.raises(ValueError, match="Unsupported transition"):
        _ = advance(Stage.RESEARCH_SCOPING, StageStatus.DONE, TransitionEvent.START)


def test_advance_rejects_unknown_transition_event_string():
    with pytest.raises(ValueError, match="not a valid TransitionEvent"):
        _ = advance(Stage.RESEARCH_SCOPING, StageStatus.PENDING, "unknown")


@pytest.mark.parametrize("stage", tuple(GATE_STAGES))
def test_gate_required_for_gate_stages_with_default_config(stage: Stage):
    assert gate_required(stage, None) is True


@pytest.mark.parametrize("stage", tuple(GATE_STAGES))
def test_gate_required_respects_hitl_stage_subset(stage: Stage):
    required = (3, 11)
    assert gate_required(stage, required) is (int(stage) in required)


@pytest.mark.parametrize("stage", tuple(s for s in Stage if s not in GATE_STAGES))
def test_gate_required_is_false_for_non_gate_stages(stage: Stage):
    assert gate_required(stage, (3, 6, 11)) is False


@pytest.mark.parametrize(
    "stage,expected",
    [
        (Stage.LITERATURE_SCREEN, Stage.SEARCH_COLLECT),
        (Stage.EXPERIMENT_DESIGN, Stage.HYPOTHESIS_SYNTHESIS),
        (Stage.QUALITY_CHECK, Stage.PAPER_WRITE),
    ],
)
def test_default_rollback_stage_for_known_gate_mappings(stage: Stage, expected: Stage):
    assert default_rollback_stage(stage) is expected


def test_default_rollback_stage_for_unknown_stage_uses_previous_stage():
    assert default_rollback_stage(Stage.KNOWLEDGE_EXTRACT) is Stage.LITERATURE_SCREEN


def test_default_rollback_stage_for_first_stage_returns_self():
    assert default_rollback_stage(Stage.RESEARCH_SCOPING) is Stage.RESEARCH_SCOPING


def test_transition_outcome_field_values_are_exposed():
    outcome = TransitionOutcome(
        stage=Stage.RESEARCH_SCOPING,
        status=StageStatus.RUNNING,
        next_stage=Stage.RESEARCH_SCOPING,
        rollback_stage=Stage.RESEARCH_SCOPING,
        checkpoint_required=True,
        decision="block",
    )

    assert outcome.checkpoint_required is True
    assert outcome.decision == "block"


def test_sequence_and_neighbor_maps_are_consistent_for_all_stages():
    for idx, stage in enumerate(STAGE_SEQUENCE):
        expected_prev = STAGE_SEQUENCE[idx - 1] if idx > 0 else None
        expected_next = (
            STAGE_SEQUENCE[idx + 1] if idx + 1 < len(STAGE_SEQUENCE) else None
        )
        assert PREVIOUS_STAGE[stage] is expected_prev
        assert NEXT_STAGE[stage] is expected_next


def test_transition_map_covers_all_stage_status_values():
    assert set(TRANSITION_MAP.keys()) == set(StageStatus)
    for source_status, targets in TRANSITION_MAP.items():
        assert isinstance(targets, frozenset)
        assert all(target in StageStatus for target in targets)
        if source_status is StageStatus.DONE:
            assert targets == frozenset()


# ── DECISION_ROLLBACK tests ──


def test_decision_rollback_has_pivot_and_refine():
    assert "pivot" in DECISION_ROLLBACK
    assert "refine" in DECISION_ROLLBACK


def test_decision_rollback_pivot_targets_hypothesis_synthesis():
    assert DECISION_ROLLBACK["pivot"] is Stage.HYPOTHESIS_SYNTHESIS


def test_decision_rollback_refine_targets_experiment_execute():
    assert DECISION_ROLLBACK["refine"] is Stage.EXPERIMENT_EXECUTE


def test_max_decision_pivots_is_positive():
    assert MAX_DECISION_PIVOTS >= 1
