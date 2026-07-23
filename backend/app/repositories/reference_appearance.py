from app.models.reference_appearance import ReferenceAppearance
from app.repositories.base import SQLAlchemyRepository


class ReferenceAppearanceRepository(SQLAlchemyRepository[ReferenceAppearance]):
    model = ReferenceAppearance
