import uuid

from sqlalchemy import desc, select

from app.models.dose_event import DoseEvent
from app.repositories.base import SQLAlchemyRepository


class DoseEventRepository(SQLAlchemyRepository[DoseEvent]):
    model = DoseEvent

    async def list_for_profile(
        self, profile_id: uuid.UUID, limit: int = 50
    ) -> list[DoseEvent]:
        stmt = (
            select(DoseEvent)
            .where(DoseEvent.profile_id == profile_id)
            .order_by(desc(DoseEvent.ts))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
