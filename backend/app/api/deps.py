import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_profile_id
from app.repositories.caregiver_link import CaregiverLinkRepository
from app.repositories.dose_event import DoseEventRepository
from app.repositories.medication import MedicationRepository
from app.repositories.profile import ProfileRepository
from app.repositories.reference_appearance import ReferenceAppearanceRepository
from app.repositories.schedule import ScheduleRepository
from app.services.caregiver_link import CaregiverLinkService
from app.services.dose_event import DoseEventService
from app.services.medication import MedicationService
from app.services.profile import ProfileService
from app.services.reference_appearance import ReferenceAppearanceService
from app.services.schedule import ScheduleService

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
CurrentProfileId = Annotated[uuid.UUID, Depends(get_current_profile_id)]


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
