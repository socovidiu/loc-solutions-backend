import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.services.job_service import JobService
from app.models.job import (
    JobCreateRequest,
    JobCreateResponse,
    JobStatusResponse,
    JobResultResponse,
    JobStatus,
)

router = APIRouter()


@router.post("", response_model=JobCreateResponse)
def create_job_endpoint(payload: JobCreateRequest, db: Session = Depends(get_db)):
    svc = JobService(db)
    job = svc.create_job(payload)
    return JobCreateResponse(job_id=job.id, status=JobStatus(job.status), created_at=job.created_at)


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_endpoint(job_id: str, db: Session = Depends(get_db)):
    svc = JobService(db)
    job = svc.get_job(job_id)

    return JobStatusResponse(
        job_id=job.id,
        status=JobStatus(job.status),
        source_locale=job.source_locale,
        target_locales=job.target_locales,
        updated_at=job.updated_at,
        created_at=job.created_at,
        error=job.error,
        external={
            "tms_provider": job.tms_provider,
            "tms_job_id": job.tms_job_id,
            "tms_project_id": None,
        },
    )

@router.get("/{job_id}/result", response_model=JobResultResponse)
def get_result_endpoint(job_id: str, db: Session = Depends(get_db)):
    svc = JobService(db)
    job = svc.get_job(job_id)

    return JobResultResponse(
        job_id=job.id,
        status=JobStatus(job.status),
        translated_content=job.translated_content,
        qc_report=job.qc_report,
        updated_at=job.updated_at,
    )
