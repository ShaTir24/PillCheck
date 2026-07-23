import uuid

import pytest
from fastapi import HTTPException

from app.models.dose_event import DoseEvent, DoseEventResult
from app.schemas.dose_event import DoseEventCreate, PerPillResult
from app.services.dose_event import DoseEventService


class FakeDoseEventRepo:
    def __init__(self) -> None:
        self.saved: list[DoseEvent] = []

    async def add(self, entity: DoseEvent) -> DoseEvent:
        self.saved.append(entity)
        return entity


async def test_match_result_with_no_per_pill_data_is_allowed() -> None:
    """CANNOT_IDENTIFY / MANUAL_TAKEN events legitimately carry no per-pill detail."""
    service = DoseEventService(FakeDoseEventRepo())

    event = await service.record(
        uuid.uuid4(), DoseEventCreate(result=DoseEventResult.CANNOT_IDENTIFY)
    )

    assert event.result == DoseEventResult.CANNOT_IDENTIFY


async def test_match_result_consistent_with_per_pill_decisions_is_allowed() -> None:
    service = DoseEventService(FakeDoseEventRepo())

    event = await service.record(
        uuid.uuid4(),
        DoseEventCreate(
            result=DoseEventResult.MATCH,
            per_pill=[PerPillResult(bbox=[0, 0, 1, 1], top_k=[], decision="match")],
        ),
    )

    assert event.result == DoseEventResult.MATCH


async def test_match_result_inconsistent_with_per_pill_decision_is_rejected() -> None:
    """FR-4 safety guard: PillCheck must never accept a MATCH the client itself
    flagged as mismatched at the per-pill level — this is the one rule in the
    whole scaffold standing in for "never confidently mis-verify"."""
    service = DoseEventService(FakeDoseEventRepo())

    with pytest.raises(HTTPException) as exc_info:
        await service.record(
            uuid.uuid4(),
            DoseEventCreate(
                result=DoseEventResult.MATCH,
                per_pill=[PerPillResult(bbox=[0, 0, 1, 1], top_k=[], decision="mismatch")],
            ),
        )

    assert exc_info.value.status_code == 422
