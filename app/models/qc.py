# app/models/qc.py
from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class QcSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class QcIssue(BaseModel):
    severity: QcSeverity
    code: str = Field(..., examples=["PLACEHOLDER_MISMATCH", "NUMBER_CHANGED"])
    message: str
    source: str | None = None
    target: str | None = None
    path: str | None = Field(
        default=None,
        description="Where the issue occurred in the content (e.g. JSON pointer / key path).",
        examples=["$.home.title"]
    )
    details: dict[str, Any] | None = None


class QcReport(BaseModel):
    passed: bool
    score: float | None = Field(default=None, ge=0, le=100)
    issues: list[QcIssue] = Field(default_factory=list)
    model: str | None = Field(default=None, description="LLM model used for QC, if applicable.")
