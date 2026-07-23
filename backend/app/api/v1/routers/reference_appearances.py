from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_reference_appearance_service
from app.schemas.reference_appearance import ReferenceAppearanceCreate, ReferenceAppearanceRead
from app.services.reference_appearance import ReferenceAppearanceService

router = APIRouter(prefix="/reference-appearances", tags=["reference-appearances"])

ReferenceAppearanceServiceDep = Annotated[
    ReferenceAppearanceService, Depends(get_reference_appearance_service)
]


@router.post("", response_model=ReferenceAppearanceRead, status_code=status.HTTP_201_CREATED)
async def create_reference_appearance(
    data: ReferenceAppearanceCreate, service: ReferenceAppearanceServiceDep
) -> ReferenceAppearanceRead:
    return await service.create(data)  # type: ignore[return-value]


@router.get("", response_model=list[ReferenceAppearanceRead])
async def list_library_appearances(
    service: ReferenceAppearanceServiceDep,
) -> list[ReferenceAppearanceRead]:
    """Bundled reference library only — user-enrolled entries (FR-14) stay device-private."""
    return await service.list_library()  # type: ignore[return-value]
