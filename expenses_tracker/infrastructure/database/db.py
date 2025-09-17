from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
)

from expenses_tracker.core.settings import get_settings


def create_sqlalchemy_engine() -> AsyncEngine:
    return create_async_engine(
        get_settings().async_postgres_url,
        echo=get_settings().database_echo,
        echo_pool=get_settings().database_pool_echo,
        pool_size=get_settings().pool_size,
    )


def create_psycopg_dsn() -> str:
    return get_settings().sync_postgres_url
