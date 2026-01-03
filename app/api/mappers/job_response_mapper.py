from __future__ import annotations

from datetime import datetime

from app.domain.job import JobEntity
from app.models.job import JobCreateResponse, JobStatusResponse, JobResultResponse, JobStatus


def to_create_response(job: JobEntity) -> JobCreateResponse:
    return JobCreateResponse(
        job_id=job.id,
        status=job.status,
        created_at=job.created_at or datetime.utcnow(),
    )


def to_status_response(job: JobEntity) -> JobStatusResponse:
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        source_locale=str(job.source_locale),
        target_locales=[str(x) for x in job.target_locales],
        tms_provider=str(job.external.tms_provider) if job.external.tms_provider else None,
        tms_job_id=job.external.tms_job_id,
        created_at=job.created_at,
        updated_at=job.updated_at,
        error=job.error,
    )


def to_result_response(job: JobEntity) -> JobResultResponse:
    return JobResultResponse(
        job_id=job.id,
        status=job.status,
        translated_content=job.translated_content,
        qc_report=job.qc_report,
        updated_at=job.updated_at,
    )
