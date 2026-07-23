import uuid
from datetime import time as time_

from sqlalchemy import ARRAY, Boolean, ForeignKey, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Schedule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A dose window for a medication. PRD FR-5 ("dose count, schedule windows")."""

    __tablename__ = "schedules"

    medication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medications.id", ondelete="CASCADE"), index=True
    )
    # e.g. "morning", "bedtime" — shown in UF-1's "Verify tonight's dose" CTA.
    window_label: Mapped[str] = mapped_column(String(40))
    time_of_day: Mapped[time_] = mapped_column(Time)
    days_of_week: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
    dose_count: Mapped[int] = mapped_column(Integer, default=1)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
