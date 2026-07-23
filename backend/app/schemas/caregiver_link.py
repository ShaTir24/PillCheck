import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.caregiver_link import CaregiverLinkStatus


class CaregiverLinkCreate(BaseModel):
    scopes: list[str] = ["summary:read"]


class CaregiverLinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_profile_id: uuid.UUID
    caregiver_profile_id: uuid.UUID | None
    invite_token: str
    scopes: list[str]
    status: CaregiverLinkStatus
    revoked_at: datetime | None
    created_at: datetime
