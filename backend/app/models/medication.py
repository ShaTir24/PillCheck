import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Medication(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A medication in a profile's regimen. PRD §11.2, FR-5."""

    __tablename__ = "medications"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), index=True
    )
    drug_name: Mapped[str] = mapped_column(String(200))
    strength: Mapped[str | None] = mapped_column(String(60))
    form: Mapped[str | None] = mapped_column(String(60))
    # Primary external key for future NDC/Pillbox and P2 FHIR integration (PRD §3, §11.2).
    ndc: Mapped[str | None] = mapped_column(String(20), index=True)

    appearance_front_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reference_appearances.id")
    )
    appearance_back_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reference_appearances.id")
    )
