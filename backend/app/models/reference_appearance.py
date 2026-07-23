import enum
import uuid

from sqlalchemy import Boolean, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Side(enum.StrEnum):
    FRONT = "front"
    BACK = "back"


class Origin(enum.StrEnum):
    LIBRARY = "library"
    USER_ENROLLED = "user_enrolled"


class ReferenceAppearance(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Bundled-library or private few-shot (FR-14) pill appearance record. PRD §11.2.

    NOTE: the metric-learning embedding vector is NOT stored here — it lives in the
    on-device FAISS index (build pipeline artifact, PRD §10.2/§10.3 `ref_index/`), not
    in Postgres. This table is metadata only, matched to that index by `id`.
    """

    __tablename__ = "reference_appearances"

    ndc: Mapped[str | None] = mapped_column(String(20), index=True)
    side: Mapped[Side] = mapped_column(Enum(Side, native_enum=False))
    imprint: Mapped[str | None] = mapped_column(String(60))
    shape: Mapped[str | None] = mapped_column(String(40))
    color: Mapped[str | None] = mapped_column(String(40))
    size_mm: Mapped[float | None] = mapped_column(Float)
    scored: Mapped[bool] = mapped_column(Boolean, default=False)
    image_uri: Mapped[str] = mapped_column(String(500))
    origin: Mapped[Origin] = mapped_column(Enum(Origin, native_enum=False))

    # Set only when origin == USER_ENROLLED (FR-14 private few-shot entries).
    owner_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE")
    )
