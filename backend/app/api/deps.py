import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.email import EmailSender, LoggingEmailSender
from app.core.security import decode_token, extract_bearer_token
from app.models.user import User
from app.repositories.caregiver_link import CaregiverLinkRepository
from app.repositories.dose_event import DoseEventRepository
from app.repositories.medication import MedicationRepository
from app.repositories.profile import ProfileRepository
from app.repositories.reference_appearance import ReferenceAppearanceRepository
from app.repositories.schedule import ScheduleRepository
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.caregiver_link import CaregiverLinkService
from app.services.dose_event import DoseEventService
from app.services.medication import MedicationService
from app.services.profile import ProfileService
from app.services.reference_appearance import ReferenceAppearanceService
from app.services.schedule import ScheduleService

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    session: DbSession, token: Annotated[str, Depends(extract_bearer_token)]
) -> User:
    payload = decode_token(token, expected_type="access")
    user = await UserRepository(session).get(payload.user_id)
    if user is None or user.token_version != payload.token_version:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_profile_id(user: CurrentUser, session: DbSession) -> uuid.UUID:
    profile = await ProfileRepository(session).get_first_for_user(user.id)
    if profile is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No profile yet — create one first")
    return profile.id


CurrentProfileId = Annotated[uuid.UUID, Depends(get_current_profile_id)]


def get_email_sender() -> EmailSender:
    return LoggingEmailSender()


EmailSenderDep = Annotated[EmailSender, Depends(get_email_sender)]


def get_auth_service(session: DbSession, email_sender: EmailSenderDep) -> AuthService:
    return AuthService(UserRepository(session), email_sender)


def get_profile_service(session: DbSession) -> ProfileService:
    return ProfileService(ProfileRepository(session))


def get_medication_service(session: DbSession) -> MedicationService:
    return MedicationService(MedicationRepository(session), ReferenceAppearanceRepository(session))


def get_schedule_service(session: DbSession) -> ScheduleService:
    return ScheduleService(ScheduleRepository(session))


def get_reference_appearance_service(session: DbSession) -> ReferenceAppearanceService:
    return ReferenceAppearanceService(ReferenceAppearanceRepository(session))


def get_dose_event_service(session: DbSession) -> DoseEventService:
    return DoseEventService(DoseEventRepository(session))


def get_caregiver_link_service(session: DbSession) -> CaregiverLinkService:
    return CaregiverLinkService(CaregiverLinkRepository(session))
