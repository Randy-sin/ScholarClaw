"""Maps ScholarClaw pipeline stages to MetaClaw skill categories.

Each stage maps to:
- task_type: MetaClaw's task category for skill retrieval
- skills: Preferred research-specific skills to inject
- top_k: Number of skills to inject at this stage
"""

from __future__ import annotations

from typing import Any

STAGE_SKILL_MAP: dict[str, dict[str, Any]] = {
    "research_scoping": {
        "task_type": "research",
        "skills": ["literature-search-strategy", "research-gap-identification"],
        "top_k": 4,
    },
    "search_collect": {
        "task_type": "research",
        "skills": ["literature-search-strategy"],
        "top_k": 6,
    },
    "literature_screen": {
        "task_type": "research",
        "skills": ["paper-relevance-screening"],
        "top_k": 6,
    },
    "knowledge_extract": {
        "task_type": "research",
        "skills": ["knowledge-card-extraction"],
        "top_k": 4,
    },
    "hypothesis_synthesis": {
        "task_type": "research",
        "skills": ["research-gap-identification", "hypothesis-formulation"],
        "top_k": 6,
    },
    "experiment_design": {
        "task_type": "research",
        "skills": ["experiment-design-rigor"],
        "top_k": 6,
    },
    "code_setup": {
        "task_type": "coding",
        "skills": ["hardware-aware-coding"],
        "top_k": 6,
    },
    "experiment_execute": {
        "task_type": "automation",
        "skills": ["experiment-debugging"],
        "top_k": 6,
    },
    "analysis_decision": {
        "task_type": "data_analysis",
        "skills": ["statistical-analysis", "research-pivot-decision"],
        "top_k": 6,
    },
    "paper_write": {
        "task_type": "communication",
        "skills": ["academic-writing-structure", "peer-review-methodology"],
        "top_k": 6,
    },
    "quality_check": {
        "task_type": "research",
        "skills": ["peer-review-methodology"],
        "top_k": 4,
    },
    "export_verify": {
        "task_type": "research",
        "skills": ["citation-integrity"],
        "top_k": 4,
    },
}

# Mapping from ScholarClaw lesson categories to MetaClaw skill categories.
LESSON_CATEGORY_TO_SKILL_CATEGORY: dict[str, str] = {
    "system": "automation",
    "experiment": "coding",
    "writing": "communication",
    "analysis": "data_analysis",
    "literature": "research",
    "pipeline": "automation",
}


def get_stage_config(stage_name: str) -> dict[str, Any]:
    """Return the MetaClaw skill config for a given pipeline stage.

    Falls back to a generic research config if the stage is unknown.
    """
    return STAGE_SKILL_MAP.get(
        stage_name,
        {"task_type": "research", "skills": [], "top_k": 4},
    )
