import uuid

from sqlalchemy import select

from app.models.schedule import Schedule
from app.repositories.base import SQLAlchemyRepository


class ScheduleRepository(SQLAlchemyRepository[Schedule]):
    model = Schedule

    async def list_for_medication(self, medication_id: uuid.UUID) -> list[Schedule]:
        stmt = select(Schedule).where(Schedule.medication_id == medication_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
