from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Login identity (email + password). Owns one or more Profiles — the
    people/PRD personas tracked in the app, see app/models/profile.py. ADR-006."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    # Bumped on password reset (and any future "log out everywhere") so every
    # outstanding JWT is invalidated at once — see app/core/security.py.
    token_version: Mapped[int] = mapped_column(Integer, default=0)
    # sha256 hex digest of the raw reset token sent by email; raw token never stored.
    password_reset_token_hash: Mapped[str | None] = mapped_column(String(64))
    password_reset_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
