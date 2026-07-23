import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentProfileId, get_caregiver_link_service
from app.schemas.caregiver_link import CaregiverLinkCreate, CaregiverLinkRead
from app.services.caregiver_link import CaregiverLinkService

router = APIRouter(prefix="/caregiver-links", tags=["caregiver-links"])

CaregiverLinkServiceDep = Annotated[CaregiverLinkService, Depends(get_caregiver_link_service)]


@router.post("", response_model=CaregiverLinkRead, status_code=status.HTTP_201_CREATED)
async def invite_caregiver(
    data: CaregiverLinkCreate, profile_id: CurrentProfileId, service: CaregiverLinkServiceDep
) -> CaregiverLinkRead:
    return await service.invite(profile_id, data)  # type: ignore[return-value]


@router.get("", response_model=list[CaregiverLinkRead])
async def list_my_caregiver_links(
    profile_id: CurrentProfileId, service: CaregiverLinkServiceDep
) -> list[CaregiverLinkRead]:
    """UF-5: sharing state must always be visible to the subject."""
    return await service.list_for_subject(profile_id)  # type: ignore[return-value]


@router.post("/{token}/accept", response_model=CaregiverLinkRead)
async def accept_caregiver_invite(
    token: str, profile_id: CurrentProfileId, service: CaregiverLinkServiceDep
) -> CaregiverLinkRead:
    return await service.accept(token, profile_id)  # type: ignore[return-value]


@router.post("/{link_id}/revoke", response_model=CaregiverLinkRead)
async def revoke_caregiver_link(
    link_id: uuid.UUID, service: CaregiverLinkServiceDep
) -> CaregiverLinkRead:
    """UF-5: patient one-tap revoke, works anytime."""
    link = await service.get(link_id)
    if link is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Caregiver link not found")
    return await service.revoke(link)  # type: ignore[return-value]
