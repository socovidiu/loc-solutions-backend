from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import update, select
from sqlalchemy.orm import Session

from app.db.models.job import Job as JobOrm
from app.mappers.job_mapper import orm_to_domain
from app.domain.job import JobEntity
from app.models.job import JobCreateRequest, JobStatus


def create_job(db: Session, payload: JobCreateRequest) -> JobEntity:
    job = JobOrm(
        status=JobStatus.CREATED.value,
        source_locale=payload.source_locale,
        target_locales=payload.target_locales,
        source_content=payload.content,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return orm_to_domain(job)


def get_job(db: Session, job_id: UUID) -> Optional[JobEntity]:
    orm = db.get(JobOrm, job_id)
    return orm_to_domain(orm) if orm else None


def update_job_status(db: Session, job_id: UUID, new_status: str, error: str | None = None) -> None:
    stmt = (
        update(JobOrm)
        .where(JobOrm.id == job_id)
        .values(status=new_status, error=error)
    )
    db.execute(stmt)
    db.commit()


def update_job_status_if_current(
    db: Session,
    job_id: UUID,
    *,
    expected_status: str,
    new_status: str,
) -> bool:
    stmt = (
        update(JobOrm)
        .where(JobOrm.id == job_id)
        .where(JobOrm.status == expected_status)
        .values(status=new_status)
    )
    res = db.execute(stmt)
    db.commit()
    return res.rowcount == 1


def set_tms_refs(db: Session, job_id: UUID, provider: str | None, tms_job_id: str | None) -> None:
    stmt = (
        update(JobOrm)
        .where(JobOrm.id == job_id)
        .values(tms_provider=provider, tms_job_id=tms_job_id)
    )
    db.execute(stmt)
    db.commit()


def save_translation(db: Session, job_id: UUID, translated_content: dict) -> None:
    stmt = (
        update(JobOrm)
        .where(JobOrm.id == job_id)
        .values(translated_content=translated_content)
    )
    db.execute(stmt)
    db.commit()


def save_translation_if_empty(db: Session, job_id: UUID, translated_content: dict) -> bool:
    stmt = (
        update(JobOrm)
        .where(JobOrm.id == job_id)
        .where(JobOrm.translated_content.is_(None))
        .values(translated_content=translated_content)
    )
    res = db.execute(stmt)
    db.commit()
    return res.rowcount == 1


def save_qc_report(db: Session, job_id: UUID, qc_report: dict) -> None:
    stmt = (
        update(JobOrm)
        .where(JobOrm.id == job_id)
        .values(qc_report=qc_report)
    )
    db.execute(stmt)
    db.commit()
