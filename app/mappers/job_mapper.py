from __future__ import annotations

from app.db.models.job import Job as JobOrm
from app.domain.job import JobEntity, ExternalRefs
from app.domain.types import JobId, Locale, Provider
from app.models.job import JobStatus


def orm_to_domain(j: JobOrm) -> JobEntity:
    return JobEntity(
        id=JobId(j.id),
        status=JobStatus(j.status),
        source_locale=Locale(j.source_locale),
        target_locales=[Locale(x) for x in (j.target_locales or [])],
        source_content=j.source_content or {},
        translated_content=j.translated_content,
        qc_report=j.qc_report,
        external=ExternalRefs(
            tms_provider=Provider(j.tms_provider) if j.tms_provider else None,
            tms_job_id=j.tms_job_id,
            tms_project_id=getattr(j, "tms_project_id", None),
        ),
        error=j.error,
        created_at=j.created_at,
        updated_at=j.updated_at,
    )
