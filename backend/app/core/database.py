from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

# Supabase's Supavisor transaction pooler multiplexes many client connections over
# few server ones and does NOT support server-side prepared statement reuse across
# requests — asyncpg must disable its statement cache, and SQLAlchemy must not pool
# on top of a pool (NullPool). See DECISIONS.md ADR-002. Direct/local Postgres wants
# neither of these, hence the flag rather than a hardcoded setting.
_engine_kwargs: dict[str, Any] = {"echo": settings.environment == "local"}
if settings.db_use_transaction_pooler:
    _engine_kwargs["poolclass"] = NullPool
    _engine_kwargs["connect_args"] = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }

engine = create_async_engine(settings.database_url, **_engine_kwargs)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: one session per request, committed on success.

    Closing an AsyncSession context manager does NOT commit — it only closes
    the connection, silently discarding any uncommitted transaction. Every
    write depends on this dependency committing explicitly.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
