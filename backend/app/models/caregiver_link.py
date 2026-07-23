import enum
import secrets
import uuid
from datetime import datetime

from sqlalchemy import ARRAY, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CaregiverLinkStatus(enum.StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    REVOKED = "revoked"


class CaregiverLink(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Caregiver access grant on a subject's profile. PRD FR-11, UF-5, §10.3."""

    __tablename__ = "caregiver_links"

    subject_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), index=True
    )
    caregiver_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL")
    )
    invite_token: Mapped[str] = mapped_column(
        String(64), unique=True, default=lambda: secrets.token_urlsafe(32)
    )
    # e.g. ["regimen:edit", "summary:read"] — FR-11 scoped access.
    scopes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    status: Mapped[CaregiverLinkStatus] = mapped_column(
        Enum(CaregiverLinkStatus, native_enum=False), default=CaregiverLinkStatus.PENDING
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
