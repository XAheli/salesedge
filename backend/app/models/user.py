"""User model for authentication."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import Field, SQLModel

VALID_ROLES = {"admin", "sales_manager", "sales_rep", "analyst", "viewer"}


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(max_length=255)
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    role: str = Field(default="viewer", max_length=50)
    organization: str | None = Field(default=None, max_length=255)
    timezone: str = Field(default="Asia/Kolkata")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
