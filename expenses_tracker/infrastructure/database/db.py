from typing import Callable

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)

from expenses_tracker.core.settings import settings


class DBEngine(BaseModel, arbitrary_types_allowed=True):
    async_engine: AsyncEngine
    async_session_factory: Callable[[], AsyncSession]


def get_db_engines() -> DBEngine:
    async_engine = create_async_engine(
        settings.async_postgres_url,
        echo=settings.database_echo,
        echo_pool=settings.database_pool_echo,
        pool_size=settings.pool_size,
    )
    async_session_factory = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    return DBEngine(
        async_session_factory=async_session_factory,
        async_engine=async_engine,
    )
