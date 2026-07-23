from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentProfileId, get_dose_event_service
from app.schemas.dose_event import DoseEventCreate, DoseEventRead
from app.services.dose_event import DoseEventService

router = APIRouter(prefix="/dose-events", tags=["dose-events"])

DoseEventServiceDep = Annotated[DoseEventService, Depends(get_dose_event_service)]


@router.post("", response_model=DoseEventRead, status_code=status.HTTP_201_CREATED)
async def record_dose_event(
    data: DoseEventCreate, profile_id: CurrentProfileId, service: DoseEventServiceDep
) -> DoseEventRead:
    """FR-9: log every verification attempt (mobile client already ran the on-device
    decision engine — this persists the result, it does not re-decide it)."""
    return await service.record(profile_id, data)  # type: ignore[return-value]


@router.get("", response_model=list[DoseEventRead])
async def list_my_dose_events(
    profile_id: CurrentProfileId,
    service: DoseEventServiceDep,
    limit: Annotated[int, Query(le=200)] = 50,
) -> list[DoseEventRead]:
    return await service.list_for_profile(profile_id, limit=limit)  # type: ignore[return-value]
