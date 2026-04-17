"""SQLAlchemy 2.0 async engine + session factory + declarative base."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    """Base declarativa para todos os ORM models."""


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Cria async engine com quirks do PgBouncer transaction mode (Supabase pooler).

    - `statement_cache_size=0`: obrigatório para asyncpg atrás do PgBouncer em transaction mode,
      senão prepared statements geram `prepared statement "__asyncpg_stmt_X__" already exists`.
    - `server_settings={"jit": "off"}`: evita comportamento inconsistente de plan caching.
    """
    global _engine
    if _engine is None:
        settings = get_settings()
        connect_args: dict[str, object] = {}
        if "asyncpg" in settings.database_url:
            connect_args = {
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
                "server_settings": {"jit": "off"},
            }
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.env == "dev",
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args=connect_args,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependência FastAPI. Fornece sessão com commit implícito ou rollback em erro."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
