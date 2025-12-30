from sqlalchemy.orm import Session
from sqlalchemy import update
from app.db.models.job import Job
from app.models.job import JobCreateRequest, JobStatus

def create_job(db: Session, payload: JobCreateRequest) -> Job:
    job = Job(
        status=JobStatus.CREATED.value,
        source_locale=payload.source_locale,
        target_locales=payload.target_locales,
        source_content=payload.content,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id) -> Job | None:
    return db.get(Job, job_id)

def update_job_status(db: Session, job_id, status: str, error: str | None = None) -> Job:
    job = db.get(Job, job_id)
    if not job:
        raise ValueError("Job not found")
    job.status = status
    job.error = error
    db.commit()
    db.refresh(job)
    return job

def save_translation(db: Session, job_id, translated_content: dict) -> Job:
    job = db.get(Job, job_id)
    if not job:
        raise ValueError("Job not found")
    job.translated_content = translated_content
    db.commit()
    db.refresh(job)
    return job

def save_qc_report(db: Session, job_id, qc_report: dict) -> Job:
    job = db.get(Job, job_id)
    if not job:
        raise ValueError("Job not found")
    job.qc_report = qc_report
    db.commit()
    db.refresh(job)
    return job

def set_tms_refs(db: Session, job_id, provider: str | None, tms_job_id: str | None) -> Job:
    job = db.get(Job, job_id)
    if not job:
        raise ValueError("Job not found")
    job.tms_provider = provider
    job.tms_job_id = tms_job_id
    db.commit()
    db.refresh(job)
    return job


def update_job_status_if_current(
    db: Session,
    job_id,
    *,
    expected_status: str,
    new_status: str,
) -> bool:
    """
    Atomically updates job status ONLY if current status == expected_status.
    Returns True if updated, False if no row matched (already moved on, missing, etc.)
    """
    stmt = (
        update(Job)
        .where(Job.id == job_id)
        .where(Job.status == expected_status)
        .values(status=new_status)
    )

    result = db.execute(stmt)
    db.commit()
    return result.rowcount == 1

def save_translation_if_empty(db: Session, job_id, translated_content: dict) -> bool:
    stmt = (
        update(Job)
        .where(Job.id == job_id)
        .where(Job.translated_content.is_(None))
        .values(translated_content=translated_content)
    )
    res = db.execute(stmt)
    db.commit()
    return res.rowcount == 1