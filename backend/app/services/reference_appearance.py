from app.models.reference_appearance import Origin, ReferenceAppearance
from app.repositories.reference_appearance import ReferenceAppearanceRepository
from app.schemas.reference_appearance import ReferenceAppearanceCreate


class ReferenceAppearanceService:
    def __init__(self, repo: ReferenceAppearanceRepository) -> None:
        self.repo = repo

    async def create(self, data: ReferenceAppearanceCreate) -> ReferenceAppearance:
        return await self.repo.add(ReferenceAppearance(**data.model_dump()))

    async def list_library(self) -> list[ReferenceAppearance]:
        return await self.repo.list(origin=Origin.LIBRARY)
