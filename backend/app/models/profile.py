import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Profile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A person using the app — patient (P1/P3/P4) or caregiver (P2). PRD §10.3."""

    __tablename__ = "profiles"

    # Owning login identity (ADR-006). 1 User : many Profiles, though only one
    # profile per user is created/selected today — see get_current_profile_id.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    display_name: Mapped[str] = mapped_column(String(120))
    # PRD accessibility NFR (§8): drives large-text/high-contrast/voice defaults per profile.
    accessibility_high_contrast: Mapped[bool] = mapped_column(default=False)
    accessibility_voice_output: Mapped[bool] = mapped_column(default=False)
