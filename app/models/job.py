# app/models/job.py
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    CREATED = "created"
    SUBMITTED = "submitted_to_tms"
    IN_PROGRESS = "in_progress"
    TRANSLATED = "translated"
    QC_RUNNING = "qc_running"
    DONE = "done"
    FAILED = "failed"


class JobCreateRequest(BaseModel):
    source_locale: str = Field(default="en-US", examples=["en-US"])
    target_locales: list[str] = Field(..., min_length=1, examples=[["ro-RO", "de-DE"]])

    # Demo-friendly: accept JSON content directly (later you can support file uploads / URLs)
    content: dict[str, Any] = Field(..., description="Source content to localize (demo JSON).")

    # Optional metadata (useful for dashboards)
    project: str | None = Field(default=None, examples=["Website", "Mobile App"])
    domain: str | None = Field(default=None, examples=["UI", "Legal"])
    priority: Literal["low", "normal", "high"] = "normal"


class ExternalRefs(BaseModel):
    tms_provider: str | None = None
    tms_job_id: str | None = None
    tms_project_id: str | None = None


class JobCreateResponse(BaseModel):
    job_id: UUID
    status: JobStatus
    created_at: datetime


class JobStatusResponse(BaseModel):
    job_id: UUID
    status: JobStatus
    source_locale: str
    target_locales: list[str]
    external: ExternalRefs = Field(default_factory=ExternalRefs)
    updated_at: datetime
    created_at: datetime
    error: str | None = None


class JobResultResponse(BaseModel):
    job_id: UUID
    status: JobStatus

    # Returned when ready
    translated_content: dict[str, Any] | None = None

    # QC report included when available (defined in qc.py)
    qc_report: dict[str, Any] | None = None

    updated_at: datetime
