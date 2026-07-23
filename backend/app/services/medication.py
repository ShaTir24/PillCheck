import uuid

from fastapi import HTTPException, status

from app.models.medication import Medication
from app.models.reference_appearance import Side
from app.repositories.medication import MedicationRepository
from app.repositories.reference_appearance import ReferenceAppearanceRepository
from app.schemas.medication import MedicationCreate, MedicationUpdate


class MedicationService:
    def __init__(
        self,
        repo: MedicationRepository,
        appearance_repo: ReferenceAppearanceRepository,
    ) -> None:
        self.repo = repo
        self.appearance_repo = appearance_repo

    async def _validate_appearance(self, ref_id: uuid.UUID, expected_side: Side) -> None:
        appearance = await self.appearance_repo.get(ref_id)
        if appearance is None:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, f"Unknown reference appearance {ref_id}"
            )
        if appearance.side != expected_side:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                f"Reference appearance {ref_id} is not a '{expected_side.value}' image",
            )

    async def create(self, profile_id: uuid.UUID, data: MedicationCreate) -> Medication:
        if data.appearance_front_id:
            await self._validate_appearance(data.appearance_front_id, Side.FRONT)
        if data.appearance_back_id:
            await self._validate_appearance(data.appearance_back_id, Side.BACK)
        medication = Medication(profile_id=profile_id, **data.model_dump())
        return await self.repo.add(medication)

    async def list_for_profile(self, profile_id: uuid.UUID) -> list[Medication]:
        return await self.repo.list_for_profile(profile_id)

    async def get(self, medication_id: uuid.UUID) -> Medication | None:
        return await self.repo.get(medication_id)

    async def update(self, medication: Medication, data: MedicationUpdate) -> Medication:
        updates = data.model_dump(exclude_unset=True)
        if "appearance_front_id" in updates and updates["appearance_front_id"]:
            await self._validate_appearance(updates["appearance_front_id"], Side.FRONT)
        if "appearance_back_id" in updates and updates["appearance_back_id"]:
            await self._validate_appearance(updates["appearance_back_id"], Side.BACK)
        for field, value in updates.items():
            setattr(medication, field, value)
        return await self.repo.add(medication)
