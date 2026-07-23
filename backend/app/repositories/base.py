import uuid
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class Repository(ABC, Generic[ModelT]):
    """Data-access interface. Services depend on this, never on SQLAlchemy directly —
    keeps services unit-testable with an in-memory fake and satisfies DIP (ADR-003).
    """

    @abstractmethod
    async def get(self, id: uuid.UUID) -> ModelT | None: ...

    @abstractmethod
    async def list(self, **filters: object) -> list[ModelT]: ...

    @abstractmethod
    async def add(self, entity: ModelT) -> ModelT: ...

    @abstractmethod
    async def delete(self, entity: ModelT) -> None: ...


class SQLAlchemyRepository(Repository[ModelT]):
    """Default implementation shared by every entity repository. Subclasses only need
    to set `model`; add entity-specific query methods on top when a feature needs one.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id: uuid.UUID) -> ModelT | None:
        return await self.session.get(self.model, id)

    async def list(self, **filters: object) -> list[ModelT]:
        stmt = select(self.model)
        for field, value in filters.items():
            stmt = stmt.where(getattr(self.model, field) == value)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def delete(self, entity: ModelT) -> None:
        await self.session.delete(entity)
        await self.session.flush()
