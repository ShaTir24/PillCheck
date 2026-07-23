from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Profile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A person using the app — patient (P1/P3/P4) or caregiver (P2). PRD §10.3."""

    __tablename__ = "profiles"

    display_name: Mapped[str] = mapped_column(String(120))
    # PRD accessibility NFR (§8): drives large-text/high-contrast/voice defaults per profile.
    accessibility_high_contrast: Mapped[bool] = mapped_column(default=False)
    accessibility_voice_output: Mapped[bool] = mapped_column(default=False)
