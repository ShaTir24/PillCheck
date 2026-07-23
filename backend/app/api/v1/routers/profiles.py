from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentProfileId, get_profile_service
from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate
from app.services.profile import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])

ProfileServiceDep = Annotated[ProfileService, Depends(get_profile_service)]


@router.post("", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: ProfileCreate, profile_id: CurrentProfileId, service: ProfileServiceDep
) -> ProfileRead:
    """Creates the profile row for the caller's own auth identity (id == auth
    profile id, see app/core/security.py) — this is "register me", not
    "create an arbitrary profile"."""
    return await service.create(profile_id, data)  # type: ignore[return-value]


@router.get("/me", response_model=ProfileRead)
async def get_my_profile(profile_id: CurrentProfileId, service: ProfileServiceDep) -> ProfileRead:
    profile = await service.get(profile_id)
    if profile is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Profile not found")
    return profile  # type: ignore[return-value]


@router.patch("/me", response_model=ProfileRead)
async def update_my_profile(
    data: ProfileUpdate, profile_id: CurrentProfileId, service: ProfileServiceDep
) -> ProfileRead:
    profile = await service.get(profile_id)
    if profile is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Profile not found")
    return await service.update(profile, data)  # type: ignore[return-value]
