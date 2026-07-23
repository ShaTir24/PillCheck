from fastapi import APIRouter

from app.api.v1.routers import (
    caregiver_links,
    dose_events,
    medications,
    profiles,
    reference_appearances,
    schedules,
)

api_router = APIRouter()
api_router.include_router(profiles.router)
api_router.include_router(medications.router)
api_router.include_router(schedules.router)
api_router.include_router(reference_appearances.router)
api_router.include_router(dose_events.router)
api_router.include_router(caregiver_links.router)
