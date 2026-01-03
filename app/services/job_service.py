from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.domain.types import JobId
from app.clients.tms.phrase import PhraseTmsClient
from app.core.config import Settings, get_settings
from app.models.job import JobCreateRequest, JobStatus
from app.models.webhooks import TmsWebhookEvent
from app.repos.jobs import (
    create_job,
    get_job,
    save_qc_report,
    save_translation,
    set_tms_refs,
    update_job_status,
    update_job_status_if_current,
)
from app.repos.webhook_events import try_register_webhook_event

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    JobStatus.CREATED.value: {JobStatus.SUBMITTED.value, JobStatus.FAILED.value},
    JobStatus.SUBMITTED.value: {JobStatus.IN_PROGRESS.value, JobStatus.FAILED.value},
    JobStatus.IN_PROGRESS.value: {JobStatus.TRANSLATED.value, JobStatus.FAILED.value},
    JobStatus.TRANSLATED.value: {JobStatus.QC_RUNNING.value, JobStatus.DONE.value, JobStatus.FAILED.value},
    JobStatus.QC_RUNNING.value: {JobStatus.DONE.value, JobStatus.FAILED.value},
    JobStatus.DONE.value: set(),
    JobStatus.FAILED.value: set(),
}

def can_transition(self, current: str, new: str) -> bool:
    return new in ALLOWED_TRANSITIONS.get(current, set())

def webhook_key(payload: TmsWebhookEvent) -> str:
    """Stable idempotency key."""
    if payload.event_id:
        return f"{payload.provider}:{payload.event_id}"
    return f"{payload.provider}:{payload.event}:{payload.internal_job_id}:{payload.tms_job_id or ''}"

class JobService:
    """Application service for job lifecycle orchestration."""
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.tms_client = PhraseTmsClient()

    # -------------------------
    # Jobs API
    # -------------------------

    def create_job(self, payload: JobCreateRequest):
        job = create_job(self.db, payload)

        try:
            tms_job_id = self.tms_client.create_job(
                project_id=self.settings.TMS_PROJECT_ID,
                source_locale=payload.source_locale,
                target_locales=payload.target_locales,
                content=payload.content,
            )
        except Exception as e:
            update_job_status(self.db, job.id, JobStatus.FAILED.value, error=str(e))
            raise HTTPException(status_code=502, detail="Failed to submit job to TMS")

        
        set_tms_refs(self.db, job.id, self.settings.TMS_PROVIDER, tms_job_id)
        update_job_status(self.db, job.id, JobStatus.SUBMITTED.value)
        
        return job
    
    def get_job(self, job_id: JobId):
        job = get_job(self.db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job

    # -------------------------
    # Webhook handling
    # -------------------------

    def handle_tms_webhook(self, payload: TmsWebhookEvent) -> JobId:
        """
        Updates job state based on webhook event.
        Returns the job_id.
        """
        job_id: JobId = UUID(str(payload.internal_job_id))

        # Idempotency: ignore duplicates
        key = webhook_key(payload)
        first_time = try_register_webhook_event(
            self.db,
            key=key,
            provider=payload.provider,
            event=payload.event,
            internal_job_id=str(job_id),
        )
        if not first_time:
            return job_id

        job = get_job(self.db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Internal job not found")

        # Always store refs
        set_tms_refs(self.db, job_id, payload.provider, payload.tms_job_id)

        current = job.status
        if current in (JobStatus.DONE.value, JobStatus.FAILED.value):
            return job_id

        if payload.event in ("job.submitted", "job.updated"):
            self._on_submitted_or_updated(job_id, current)
            return job_id

        if payload.event == "job.failed":
            self._on_failed(job_id, payload.error)
            return job_id

        if payload.event == "job.completed":
            self._on_completed(job_id, current, payload.translated_content)
            return job_id

        raise HTTPException(status_code=400, detail="Unknown event")
    
    def _on_submitted_or_updated(self, job_id: JobId, current_status: str) -> None:
        if not can_transition(current_status, JobStatus.IN_PROGRESS.value):
            return

        if current_status in (JobStatus.SUBMITTED.value, JobStatus.CREATED.value):
            update_job_status_if_current(
                self.db,
                job_id,
                expected_status=current_status,
                new_status=JobStatus.IN_PROGRESS.value,
            )

    def _on_failed(self, job_id: JobId, error: Optional[str]) -> None:
        update_job_status(
            self.db,
            job_id,
            JobStatus.FAILED.value,
            error=error or "TMS failed",
        )

    def _on_completed(self, job_id: JobId, current_status: str, translated_content: Optional[dict]) -> None:
        if translated_content is not None:
            save_translation(self.db, job_id, translated_content)

        if current_status in (JobStatus.TRANSLATED.value, JobStatus.QC_RUNNING.value, JobStatus.DONE.value):
            return

        if current_status in (JobStatus.IN_PROGRESS.value, JobStatus.SUBMITTED.value, JobStatus.CREATED.value):
            update_job_status_if_current(
                self.db,
                job_id,
                expected_status=current_status,
                new_status=JobStatus.TRANSLATED.value,
            )


    # ---------- QC saving (used by worker later) ----------
    def save_qc(self, job_id, qc_report: dict) -> None:
        save_qc_report(self.db, job_id, qc_report)
        update_job_status(self.db, job_id, JobStatus.DONE.value)
