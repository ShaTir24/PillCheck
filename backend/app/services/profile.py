import uuid

from app.models.profile import Profile
from app.repositories.profile import ProfileRepository
from app.schemas.profile import ProfileCreate, ProfileUpdate


class ProfileService:
    def __init__(self, repo: ProfileRepository) -> None:
        self.repo = repo

    async def create(self, user_id: uuid.UUID, data: ProfileCreate) -> Profile:
        return await self.repo.add(Profile(user_id=user_id, **data.model_dump()))

    async def get(self, profile_id: uuid.UUID) -> Profile | None:
        return await self.repo.get(profile_id)

    async def update(self, profile: Profile, data: ProfileUpdate) -> Profile:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
        return await self.repo.add(profile)
