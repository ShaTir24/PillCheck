import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.dose_event import DoseEventResult


class PerPillCandidate(BaseModel):
    ref_id: uuid.UUID
    embed_sim: float
    imprint_conf: float | None = None
    fused_score: float


class PerPillResult(BaseModel):
    bbox: list[float]
    top_k: list[PerPillCandidate]
    decision: str


class DoseEventCreate(BaseModel):
    scheduled_window_id: uuid.UUID | None = None
    result: DoseEventResult
    per_pill: list[PerPillResult] = []
    quality: dict[str, Any] = {}
    image_uri: str | None = None


class DoseEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    profile_id: uuid.UUID
    ts: datetime
    scheduled_window_id: uuid.UUID | None
    result: DoseEventResult
    per_pill: list[dict[str, Any]]
    quality: dict[str, Any]
    image_uri: str | None
    created_at: datetime
