from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


ContentModality = Literal["text", "image", "video"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GenerationRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    audience: str = "general beginner"
    user_id: str = "default"
    style: str = "clear, engaging popular science"
    source_text: str | None = None
    max_iterations: int | None = None
    llm_backend: str | None = None


class Artifact(BaseModel):
    id: str = Field(default_factory=lambda: f"artifact_{uuid4().hex[:8]}")
    modality: ContentModality
    title: str
    path: str
    mime_type: str
    metadata: dict = Field(default_factory=dict)


class ArticleDraft(BaseModel):
    title: str
    synopsis: str
    content: str


class FeedbackIssue(BaseModel):
    issue: str
    impact: int = Field(ge=1, le=10)
    evidence: str
    suggestion: str


class StudentFeedback(BaseModel):
    comprehension_score: int = Field(ge=1, le=10)
    interest_score: int = Field(ge=1, le=10)
    restatement: str
    confusion_points: list[FeedbackIssue] = Field(default_factory=list)
    recommendation: Literal["continue", "stop"] = "continue"


class AggregatedFeedback(BaseModel):
    common_issues: list[FeedbackIssue] = Field(default_factory=list)
    must_fix: list[FeedbackIssue] = Field(default_factory=list)
    nice_to_have: list[FeedbackIssue] = Field(default_factory=list)
    summary: str = ""


class FactCheckReport(BaseModel):
    blocking_issues: list[FeedbackIssue] = Field(default_factory=list)
    warnings: list[FeedbackIssue] = Field(default_factory=list)
    summary: str = ""


class IterationState(BaseModel):
    iteration: int
    draft_path: str
    feedback_path: str | None = None
    aggregate_path: str | None = None
    clarity_score: int = 1
    high_impact_issue_count: int = 0
    created_at: str = Field(default_factory=utc_now)


class GenerationResult(BaseModel):
    run_id: str
    user_id: str
    topic: str
    audience: str
    final_article: ArticleDraft
    artifacts: list[Artifact]
    iterations: list[IterationState]
    fact_check: FactCheckReport
    memory_updates: list[str] = Field(default_factory=list)
    run_dir: str
    created_at: str = Field(default_factory=utc_now)


class MemorySearchResult(BaseModel):
    path: str
    title: str
    summary: str
    tags: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    score: float = 0.0


class RunPaths(BaseModel):
    run_id: str
    run_dir: Path
    drafts_dir: Path
    feedback_dir: Path
    final_dir: Path
