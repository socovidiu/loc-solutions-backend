import json
from uuid import UUID
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
from app.api.mappers.job_response_mapper import (
    to_create_response,
    to_status_response,
    to_result_response, 
)

router = APIRouter()


@router.post("", response_model=JobCreateResponse)
def create_job_endpoint(payload: JobCreateRequest, db: Session = Depends(get_db)):
    svc = JobService(db)
    job = svc.create_job(payload)
    return to_create_response(job)


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_endpoint(job_id: UUID, db: Session = Depends(get_db)):
    svc = JobService(db)
    job = svc.get_job(job_id)
    return to_status_response(job)

@router.get("/{job_id}/result", response_model=JobResultResponse)
def get_result_endpoint(job_id: UUID, db: Session = Depends(get_db)):
    svc = JobService(db)
    job = svc.get_job(job_id)
    return to_result_response(job)
