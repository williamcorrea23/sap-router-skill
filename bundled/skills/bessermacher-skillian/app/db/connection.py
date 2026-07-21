"""Database connection and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.db.models import Base

_engine = None
_async_session_factory = None


def _get_engine(force_new: bool = False):
    """Get or create the async engine."""
    global _engine
    if _engine is None or force_new:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
        )
    return _engine


def _get_session_factory(force_new: bool = False):
    """Get or create the session factory."""
    global _async_session_factory
    if _async_session_factory is None or force_new:
        _async_session_factory = async_sessionmaker(
            bind=_get_engine(force_new),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_factory


async def init_db() -> None:
    """Initialize database tables."""
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    global _engine, _async_session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency for database sessions."""
    session_factory = _get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
