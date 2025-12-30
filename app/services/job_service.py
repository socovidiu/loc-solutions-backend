from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.clients.tms.phrase import PhraseTmsClient
from app.models.job import JobCreateRequest, JobStatus
from app.models.webhooks import TmsWebhookEvent

from app.repos.jobs import (
    create_job,
    get_job,
    update_job_status,
    save_translation,
    save_qc_report,
    set_tms_refs,
    update_job_status_if_current,  
)

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "created": {"submitted_to_tms", "failed"},
    "submitted_to_tms": {"in_progress", "failed"},
    "in_progress": {"translated", "failed"},
    "translated": {"qc_running", "done", "failed"},
    "qc_running": {"done", "failed"},
    "done": set(),
    "failed": set(),
}

def _can_transition(self, current: str, new: str) -> bool:
    return new in ALLOWED_TRANSITIONS.get(current, set())

class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.tms_client = PhraseTmsClient()

    # ---------- Jobs API ----------
    def create_job(self, payload: JobCreateRequest):
        job = create_job(self.db, payload)

        tms_job_id = self.tms_client.create_job(
            project_id=self.settings.TMS_PROJECT_ID,
            source_locale=payload.source_locale,
            target_locales=payload.target_locales,
            content=payload.content,
        )
        
        set_tms_refs(self.db, job.id, self.settings.TMS_PROVIDER, tms_job_id)
        update_job_status(self.db, job.id, JobStatus.SUBMITTED.value)
        
        return job
    
    def get_job(self, job_id):
        job = get_job(self.db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job

    # ---------- Webhook handling ----------
    def handle_tms_webhook(self, payload: TmsWebhookEvent) -> str:
        """
        Updates job state based on webhook event.
        Returns the job_id.
        """
        # Ensure job exists
        job = get_job(self.db, payload.internal_job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Internal job not found")

        # Track TMS refs
        set_tms_refs(self.db, payload.internal_job_id, payload.provider, payload.tms_job_id)

        current = job.status

        # If job is terminal, ignore webhook
        if current in (JobStatus.DONE.value, JobStatus.FAILED.value):
            return payload.internal_job_id

        if payload.event in ("job.submitted", "job.updated"):
            # If we're already beyond in_progress, ignore
            if not self._can_transition(current, JobStatus.IN_PROGRESS.value):
                return payload.internal_job_id

            # Only advance if current matches what we expect in the workflow
            # For demo, allow submitted_to_tms or created -> in_progress (depending on your flow)
            if current == JobStatus.SUBMITTED.value:
                update_job_status_if_current(
                    self.db, payload.internal_job_id,
                    expected_status=JobStatus.SUBMITTED.value,
                    new_status=JobStatus.IN_PROGRESS.value,
                )
            elif current == JobStatus.CREATED.value:
                update_job_status_if_current(
                    self.db, payload.internal_job_id,
                    expected_status=JobStatus.CREATED.value,
                    new_status=JobStatus.IN_PROGRESS.value,
                )
            return payload.internal_job_id

        if payload.event == "job.failed":
            # Only fail if not terminal
            update_job_status(self.db, payload.internal_job_id, JobStatus.FAILED.value, error=payload.error or "TMS failed")
            return payload.internal_job_id

        if payload.event == "job.completed":
            # If already translated or beyond, ignore duplicate completion events
            if current in (JobStatus.TRANSLATED.value, JobStatus.QC_RUNNING.value, JobStatus.DONE.value):
                return payload.internal_job_id

            # Save translation once (safe overwrite is usually OK; you can also guard it)
            if payload.translated_content is not None:
                save_translation(self.db, payload.internal_job_id, payload.translated_content)

            # Only move in_progress -> translated (or submitted/created -> translated if your TMS skips states)
            if current == JobStatus.IN_PROGRESS.value:
                update_job_status_if_current(
                    self.db, payload.internal_job_id,
                    expected_status=JobStatus.IN_PROGRESS.value,
                    new_status=JobStatus.TRANSLATED.value,
                )
            elif current == JobStatus.SUBMITTED.value:
                update_job_status_if_current(
                    self.db, payload.internal_job_id,
                    expected_status=JobStatus.SUBMITTED.value,
                    new_status=JobStatus.TRANSLATED.value,
                )
            elif current == JobStatus.CREATED.value:
                update_job_status_if_current(
                    self.db, payload.internal_job_id,
                    expected_status=JobStatus.CREATED.value,
                    new_status=JobStatus.TRANSLATED.value,
                )

            return payload.internal_job_id

        raise HTTPException(status_code=400, detail="Unknown event")

    # ---------- QC saving (used by worker later) ----------
    def save_qc(self, job_id, qc_report: dict):
        save_qc_report(self.db, job_id, qc_report)
        update_job_status(self.db, job_id, JobStatus.DONE.value)
