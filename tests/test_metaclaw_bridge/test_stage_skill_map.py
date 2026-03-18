"""Tests for stage-skill mapping module."""

from scholarclaw_engine.metaclaw_bridge.stage_skill_map import (
    STAGE_SKILL_MAP,
    LESSON_CATEGORY_TO_SKILL_CATEGORY,
    get_stage_config,
)


def test_all_12_stages_mapped():
    """All 12 pipeline stages should have a mapping entry."""
    expected_stages = [
        "research_scoping", "search_collect", "literature_screen",
        "knowledge_extract", "hypothesis_synthesis", "experiment_design",
        "code_setup", "experiment_execute", "analysis_decision",
        "paper_write", "quality_check", "export_verify",
    ]
    for stage in expected_stages:
        assert stage in STAGE_SKILL_MAP, f"Missing mapping for {stage}"


def test_stage_config_has_required_keys():
    """Each stage config should have task_type, skills, and top_k."""
    for stage_name, config in STAGE_SKILL_MAP.items():
        assert "task_type" in config, f"{stage_name} missing task_type"
        assert "skills" in config, f"{stage_name} missing skills"
        assert "top_k" in config, f"{stage_name} missing top_k"
        assert isinstance(config["skills"], list)
        assert isinstance(config["top_k"], int)
        assert config["top_k"] > 0


def test_get_stage_config_known():
    cfg = get_stage_config("hypothesis_synthesis")
    assert cfg["task_type"] == "research"
    assert "hypothesis-formulation" in cfg["skills"]


def test_get_stage_config_unknown_returns_default():
    cfg = get_stage_config("nonexistent_stage")
    assert cfg["task_type"] == "research"
    assert cfg["top_k"] == 4


def test_lesson_category_mapping_complete():
    """All lesson categories should map to a skill category."""
    expected = ["system", "experiment", "writing", "analysis", "literature", "pipeline"]
    for cat in expected:
        assert cat in LESSON_CATEGORY_TO_SKILL_CATEGORY
