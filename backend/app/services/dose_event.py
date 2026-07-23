import uuid

from fastapi import HTTPException, status

from app.models.dose_event import DoseEvent, DoseEventResult
from app.repositories.dose_event import DoseEventRepository
from app.schemas.dose_event import DoseEventCreate


class DoseEventService:
    def __init__(self, repo: DoseEventRepository) -> None:
        self.repo = repo

    async def record(self, profile_id: uuid.UUID, data: DoseEventCreate) -> DoseEvent:
        self._validate_consistency(data)
        event = DoseEvent(
            profile_id=profile_id,
            scheduled_window_id=data.scheduled_window_id,
            result=data.result,
            per_pill=[p.model_dump(mode="json") for p in data.per_pill],
            quality=data.quality,
            image_uri=data.image_uri,
        )
        return await self.repo.add(event)

    def _validate_consistency(self, data: DoseEventCreate) -> None:
        """FR-4 safety guard: a MATCH result is never accepted if any per-pill
        candidate disagrees — the on-device decision engine owns the real logic,
        this is a server-side integrity check against a client that's wrong or lying.
        """
        if data.result != DoseEventResult.MATCH:
            return
        if any(p.decision != "match" for p in data.per_pill):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                "result=MATCH is inconsistent with a non-matching per-pill decision",
            )

    async def list_for_profile(self, profile_id: uuid.UUID, limit: int = 50) -> list[DoseEvent]:
        return await self.repo.list_for_profile(profile_id, limit=limit)
