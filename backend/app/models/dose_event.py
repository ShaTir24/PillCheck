import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DoseEventResult(enum.StrEnum):
    MATCH = "match"
    MISMATCH = "mismatch"
    CANNOT_IDENTIFY = "cannot_identify"
    MANUAL_TAKEN = "manual_taken"


class DoseEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One verification attempt. PRD §11.2, FR-9, FR-4."""

    __tablename__ = "dose_events"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), index=True
    )
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Null for identify-only mode (FR-6).
    scheduled_window_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schedules.id", ondelete="SET NULL")
    )
    result: Mapped[DoseEventResult] = mapped_column(Enum(DoseEventResult, native_enum=False))
    # [{bbox, top_k:[{ref_id, embed_sim, imprint_conf, fused_score}], decision}]
    per_pill: Mapped[list[Any]] = mapped_column(JSON, default=list)
    # blur/exposure/resolution metrics feeding abstention analysis (§13).
    quality: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    # Only set with explicit opt-in (PRD §11.3 data governance).
    image_uri: Mapped[str | None] = mapped_column(String(500))
