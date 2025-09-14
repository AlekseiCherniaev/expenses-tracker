from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from expenses_tracker.core.settings import settings

engine = create_async_engine(
    settings.async_postgres_url,
    echo=settings.database_echo,
    echo_pool=settings.database_pool_echo,
    pool_size=settings.pool_size,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
