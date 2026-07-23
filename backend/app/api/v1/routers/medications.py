import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentProfileId, get_medication_service
from app.schemas.medication import MedicationCreate, MedicationRead, MedicationUpdate
from app.services.medication import MedicationService

router = APIRouter(prefix="/medications", tags=["medications"])

MedicationServiceDep = Annotated[MedicationService, Depends(get_medication_service)]


@router.post("", response_model=MedicationRead, status_code=status.HTTP_201_CREATED)
async def create_medication(
    data: MedicationCreate, profile_id: CurrentProfileId, service: MedicationServiceDep
) -> MedicationRead:
    return await service.create(profile_id, data)  # type: ignore[return-value]


@router.get("", response_model=list[MedicationRead])
async def list_my_medications(
    profile_id: CurrentProfileId, service: MedicationServiceDep
) -> list[MedicationRead]:
    return await service.list_for_profile(profile_id)  # type: ignore[return-value]


@router.get("/{medication_id}", response_model=MedicationRead)
async def get_medication(medication_id: uuid.UUID, service: MedicationServiceDep) -> MedicationRead:
    medication = await service.get(medication_id)
    if medication is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Medication not found")
    return medication  # type: ignore[return-value]


@router.patch("/{medication_id}", response_model=MedicationRead)
async def update_medication(
    medication_id: uuid.UUID, data: MedicationUpdate, service: MedicationServiceDep
) -> MedicationRead:
    medication = await service.get(medication_id)
    if medication is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Medication not found")
    return await service.update(medication, data)  # type: ignore[return-value]
