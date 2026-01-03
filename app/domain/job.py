from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from app.models.job import JobStatus
from app.domain.types import JobId, Locale, Provider


@dataclass(frozen=True)
class ExternalRefs:
    tms_provider: Optional[Provider] = None
    tms_job_id: Optional[str] = None
    tms_project_id: Optional[str] = None


@dataclass
class JobEntity:
    id: JobId
    status: JobStatus
    source_locale: Locale
    target_locales: list[Locale]
    source_content: dict[str, Any]

    translated_content: Optional[dict[str, Any]] = None
    qc_report: Optional[dict[str, Any]] = None

    external: ExternalRefs = ExternalRefs()
    error: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
