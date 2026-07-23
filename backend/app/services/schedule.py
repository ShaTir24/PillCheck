import uuid

from app.models.schedule import Schedule
from app.repositories.schedule import ScheduleRepository
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate


class ScheduleService:
    def __init__(self, repo: ScheduleRepository) -> None:
        self.repo = repo

    async def create(self, medication_id: uuid.UUID, data: ScheduleCreate) -> Schedule:
        schedule = Schedule(medication_id=medication_id, **data.model_dump())
        return await self.repo.add(schedule)

    async def list_for_medication(self, medication_id: uuid.UUID) -> list[Schedule]:
        return await self.repo.list_for_medication(medication_id)

    async def get(self, schedule_id: uuid.UUID) -> Schedule | None:
        return await self.repo.get(schedule_id)

    async def update(self, schedule: Schedule, data: ScheduleUpdate) -> Schedule:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(schedule, field, value)
        return await self.repo.add(schedule)
