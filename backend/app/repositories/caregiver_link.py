from sqlalchemy import select

from app.models.caregiver_link import CaregiverLink
from app.repositories.base import SQLAlchemyRepository


class CaregiverLinkRepository(SQLAlchemyRepository[CaregiverLink]):
    model = CaregiverLink

    async def get_by_token(self, token: str) -> CaregiverLink | None:
        stmt = select(CaregiverLink).where(CaregiverLink.invite_token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
