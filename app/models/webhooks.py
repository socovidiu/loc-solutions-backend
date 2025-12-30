from pydantic import BaseModel, Field
from typing import Any, Literal

class TmsWebhookEvent(BaseModel):
    provider: str = Field(default="phrase")
    event: Literal["job.submitted", "job.updated", "job.completed", "job.failed"]

    internal_job_id: str
    tms_job_id: str | None = None

    # If TMS sends a unique event id, use it (best for idempotency)
    event_id: str | None = None

    translated_content: dict[str, Any] | None = None
    error: str | None = None
