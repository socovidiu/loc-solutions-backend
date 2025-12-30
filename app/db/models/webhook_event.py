from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    # Idempotency key (event_id or hash). Primary key => unique by definition.
    key: Mapped[str] = mapped_column(String(128), primary_key=True)

    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    event: Mapped[str] = mapped_column(String(64), nullable=False)
    internal_job_id: Mapped[str] = mapped_column(String(64), nullable=False)

    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


Index("ix_webhook_events_job", WebhookEvent.internal_job_id)
