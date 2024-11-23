from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ...core.config import settings
from .base import Base

# Create async engine for SQLite
async_engine = create_async_engine(
    settings.DATABASE_URI,
    echo=settings.DB_ECHO,
    # SQLite specific: enable foreign keys
    connect_args={"check_same_thread": False}
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def init_db() -> None:
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    Dependency for getting async database sessions.
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Optional: Database health check utility
async def check_db_connected() -> bool:
    """Check if database is connected"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

async def close_db_connections() -> None:
    """Close database connections"""
    await async_engine.dispose()
