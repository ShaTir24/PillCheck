import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.models.caregiver_link import CaregiverLink, CaregiverLinkStatus
from app.repositories.caregiver_link import CaregiverLinkRepository
from app.schemas.caregiver_link import CaregiverLinkCreate


class CaregiverLinkService:
    def __init__(self, repo: CaregiverLinkRepository) -> None:
        self.repo = repo

    async def invite(
        self, subject_profile_id: uuid.UUID, data: CaregiverLinkCreate
    ) -> CaregiverLink:
        link = CaregiverLink(subject_profile_id=subject_profile_id, scopes=data.scopes)
        return await self.repo.add(link)

    async def accept(self, token: str, caregiver_profile_id: uuid.UUID) -> CaregiverLink:
        link = await self.repo.get_by_token(token)
        if link is None or link.status != CaregiverLinkStatus.PENDING:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found or already used")
        link.caregiver_profile_id = caregiver_profile_id
        link.status = CaregiverLinkStatus.ACTIVE
        return await self.repo.add(link)

    async def revoke(self, link: CaregiverLink) -> CaregiverLink:
        """PRD FR-11: subject can revoke anytime, sharing state always visible to them."""
        link.status = CaregiverLinkStatus.REVOKED
        link.revoked_at = datetime.now(UTC)
        return await self.repo.add(link)

    async def list_for_subject(self, subject_profile_id: uuid.UUID) -> list[CaregiverLink]:
        return await self.repo.list(subject_profile_id=subject_profile_id)

    async def get(self, link_id: uuid.UUID) -> CaregiverLink | None:
        return await self.repo.get(link_id)
