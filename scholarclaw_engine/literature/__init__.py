"""Real literature search and citation management for ScholarClaw.

Provides API clients for Semantic Scholar and arXiv, plus unified search
with deduplication and BibTeX generation.  All network I/O uses stdlib
``urllib`` — **zero** extra pip dependencies.
"""

from scholarclaw_engine.literature.models import Author, Paper
from scholarclaw_engine.literature.search import search_papers
from scholarclaw_engine.literature.verify import (
    CitationResult,
    VerificationReport,
    VerifyStatus,
    verify_citations,
)

__all__ = [
    "Author",
    "CitationResult",
    "Paper",
    "VerificationReport",
    "VerifyStatus",
    "search_papers",
    "verify_citations",
]
