from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.db.models.webhook_event import WebhookEvent


def try_register_webhook_event(
    db: Session,
    *,
    key: str,
    provider: str,
    event: str,
    internal_job_id: str,
) -> bool:
    """
    Returns True if this is the first time we see this event key.
    Returns False if it's a duplicate (already processed/seen).
    """
    stmt = insert(WebhookEvent).values(
        key=key,
        provider=provider,
        event=event,
        internal_job_id=internal_job_id,
    ).on_conflict_do_nothing(index_elements=["key"])

    result = db.execute(stmt)
    db.commit()
    return result.rowcount == 1
