import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_schedule_service
from app.schemas.schedule import ScheduleCreate, ScheduleRead, ScheduleUpdate
from app.services.schedule import ScheduleService

router = APIRouter(prefix="/medications/{medication_id}/schedules", tags=["schedules"])

ScheduleServiceDep = Annotated[ScheduleService, Depends(get_schedule_service)]


@router.post("", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    medication_id: uuid.UUID, data: ScheduleCreate, service: ScheduleServiceDep
) -> ScheduleRead:
    return await service.create(medication_id, data)  # type: ignore[return-value]


@router.get("", response_model=list[ScheduleRead])
async def list_schedules(
    medication_id: uuid.UUID, service: ScheduleServiceDep
) -> list[ScheduleRead]:
    return await service.list_for_medication(medication_id)  # type: ignore[return-value]


@router.patch("/{schedule_id}", response_model=ScheduleRead)
async def update_schedule(
    schedule_id: uuid.UUID, data: ScheduleUpdate, service: ScheduleServiceDep
) -> ScheduleRead:
    schedule = await service.get(schedule_id)
    if schedule is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Schedule not found")
    return await service.update(schedule, data)  # type: ignore[return-value]
