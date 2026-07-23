import uuid
from datetime import datetime, time

from pydantic import BaseModel, ConfigDict


class ScheduleBase(BaseModel):
    window_label: str
    time_of_day: time
    days_of_week: list[int] = []
    dose_count: int = 1
    active: bool = True


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    window_label: str | None = None
    time_of_day: time | None = None
    days_of_week: list[int] | None = None
    dose_count: int | None = None
    active: bool | None = None


class ScheduleRead(ScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    medication_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
