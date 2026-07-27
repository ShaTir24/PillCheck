import uuid

from sqlalchemy import select

from app.models.profile import Profile
from app.repositories.base import SQLAlchemyRepository


class ProfileRepository(SQLAlchemyRepository[Profile]):
    model = Profile

    async def get_first_for_user(self, user_id: uuid.UUID) -> Profile | None:
        """The caller's acting profile (ADR-006 scope guard: one profile per
        user is resolved deterministically until FR-12 profile-switching)."""
        stmt = (
            select(Profile).where(Profile.user_id == user_id).order_by(Profile.created_at).limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
