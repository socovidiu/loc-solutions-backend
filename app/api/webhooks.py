import hashlib
import json

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.deps import get_db
from app.models.webhooks import TmsWebhookEvent
from app.services.job_service import JobService
from app.repos.webhook_events import try_register_webhook_event

router = APIRouter()
settings = get_settings()


def verify_webhook(x_webhook_secret: str | None) -> None:
    if not settings.TMS_WEBHOOK_SECRET:
        return
    if not x_webhook_secret or x_webhook_secret != settings.TMS_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")


def compute_idempotency_key(payload: TmsWebhookEvent) -> str:
    # Prefer event_id if provided by TMS
    if payload.event_id:
        return f"{payload.provider}:{payload.event_id}"

    # Fallback: stable hash of the payload content
    body = json.dumps(payload.model_dump(), sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return f"{payload.provider}:sha256:{digest}"


@router.post("/tms")
def tms_webhook(
    payload: TmsWebhookEvent,
    x_webhook_secret: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    verify_webhook(x_webhook_secret)

    key = compute_idempotency_key(payload)
    first_time = try_register_webhook_event(
        db,
        key=key,
        provider=payload.provider,
        event=payload.event,
        internal_job_id=payload.internal_job_id,
    )

    # Duplicate webhook: return 200 OK and do nothing
    if not first_time:
        return {"ok": True, "duplicate": True}

    svc = JobService(db)
    job_id = svc.handle_tms_webhook(payload)

    return {"ok": True, "job_id": str(job_id), "duplicate": False}
