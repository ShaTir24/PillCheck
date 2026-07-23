from app.models.profile import Profile
from app.repositories.base import SQLAlchemyRepository


class ProfileRepository(SQLAlchemyRepository[Profile]):
    model = Profile
