from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuditMixin(SQLModel):
    """Mixin providing standard audit fields for all persistent models."""

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=_utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=_utcnow, nullable=False)
    created_by: str | None = Field(default=None, max_length=255)
    updated_by: str | None = Field(default=None, max_length=255)
