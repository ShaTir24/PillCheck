import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MedicationBase(BaseModel):
    drug_name: str
    strength: str | None = None
    form: str | None = None
    ndc: str | None = None
    appearance_front_id: uuid.UUID | None = None
    appearance_back_id: uuid.UUID | None = None


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(BaseModel):
    drug_name: str | None = None
    strength: str | None = None
    form: str | None = None
    ndc: str | None = None
    appearance_front_id: uuid.UUID | None = None
    appearance_back_id: uuid.UUID | None = None


class MedicationRead(MedicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    profile_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
