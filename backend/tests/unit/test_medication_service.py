import uuid

import pytest
from fastapi import HTTPException

from app.models.medication import Medication
from app.models.reference_appearance import Origin, ReferenceAppearance, Side
from app.schemas.medication import MedicationCreate
from app.services.medication import MedicationService


class FakeMedicationRepo:
    """In-memory fake — proves the repository interface is swappable (ADR-003/DIP),
    no database needed for this test."""

    def __init__(self) -> None:
        self.saved: list[Medication] = []

    async def add(self, entity: Medication) -> Medication:
        self.saved.append(entity)
        return entity


class FakeAppearanceRepo:
    def __init__(self, appearances: dict[uuid.UUID, ReferenceAppearance]) -> None:
        self._appearances = appearances

    async def get(self, id: uuid.UUID) -> ReferenceAppearance | None:
        return self._appearances.get(id)


def _appearance(side: Side) -> ReferenceAppearance:
    return ReferenceAppearance(
        id=uuid.uuid4(),
        side=side,
        image_uri="s3://ref/x.png",
        origin=Origin.LIBRARY,
    )


async def test_create_medication_accepts_matching_side() -> None:
    front = _appearance(Side.FRONT)
    service = MedicationService(FakeMedicationRepo(), FakeAppearanceRepo({front.id: front}))

    medication = await service.create(
        uuid.uuid4(),
        MedicationCreate(drug_name="Metformin", appearance_front_id=front.id),
    )

    assert medication.drug_name == "Metformin"
    assert medication.appearance_front_id == front.id


async def test_create_medication_rejects_wrong_side() -> None:
    back = _appearance(Side.BACK)
    service = MedicationService(FakeMedicationRepo(), FakeAppearanceRepo({back.id: back}))

    with pytest.raises(HTTPException) as exc_info:
        await service.create(
            uuid.uuid4(),
            MedicationCreate(drug_name="Metformin", appearance_front_id=back.id),
        )

    assert exc_info.value.status_code == 422


async def test_create_medication_rejects_unknown_appearance() -> None:
    service = MedicationService(FakeMedicationRepo(), FakeAppearanceRepo({}))

    with pytest.raises(HTTPException) as exc_info:
        await service.create(
            uuid.uuid4(),
            MedicationCreate(drug_name="Metformin", appearance_front_id=uuid.uuid4()),
        )

    assert exc_info.value.status_code == 422
