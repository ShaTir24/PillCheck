import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.reference_appearance import Origin, Side


class ReferenceAppearanceBase(BaseModel):
    ndc: str | None = None
    side: Side
    imprint: str | None = None
    shape: str | None = None
    color: str | None = None
    size_mm: float | None = None
    scored: bool = False
    image_uri: str
    origin: Origin
    owner_profile_id: uuid.UUID | None = None


class ReferenceAppearanceCreate(ReferenceAppearanceBase):
    pass


class ReferenceAppearanceRead(ReferenceAppearanceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
