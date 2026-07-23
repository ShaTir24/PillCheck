import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    display_name: str
    accessibility_high_contrast: bool = False
    accessibility_voice_output: bool = False


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    accessibility_high_contrast: bool | None = None
    accessibility_voice_output: bool | None = None


class ProfileRead(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
