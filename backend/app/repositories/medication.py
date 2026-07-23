import uuid

from sqlalchemy import select

from app.models.medication import Medication
from app.repositories.base import SQLAlchemyRepository


class MedicationRepository(SQLAlchemyRepository[Medication]):
    model = Medication

    async def list_for_profile(self, profile_id: uuid.UUID) -> list[Medication]:
        stmt = select(Medication).where(Medication.profile_id == profile_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
