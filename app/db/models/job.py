# app/db/models/job.py
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Job(Base):
    __tablename__ = "jobs"

    # Primary key as UUID (real UUID type in Postgres)
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Status (indexed for dashboard polling)
    status: Mapped[str] = mapped_column(String(32), default="created", index=True)

    source_locale: Mapped[str] = mapped_column(String(32), nullable=False)

    # Store list directly as JSONB
    target_locales: Mapped[list[str]] = mapped_column(JSONB, nullable=False)

    # Store content blobs as JSONB (queryable + indexable if needed)
    source_content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    translated_content: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # QC report as JSONB
    qc_report: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # TMS mapping
    tms_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tms_job_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )


# Optional: explicit indexes (Postgres-friendly)
Index("ix_jobs_tms_job_id", Job.tms_job_id)
Index("ix_jobs_created_at", Job.created_at)
