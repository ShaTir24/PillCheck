from sqlalchemy import select

from app.models.user import User
from app.repositories.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_reset_token_hash(self, token_hash: str) -> User | None:
        stmt = select(User).where(User.password_reset_token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
