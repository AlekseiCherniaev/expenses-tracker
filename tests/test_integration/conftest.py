from pytest_asyncio import fixture
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer

from expenses_tracker.infrastructure.database.models import Base


@fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres


@fixture
async def async_engine(postgres_container):
    url = postgres_container.get_connection_url().replace("psycopg2", "asyncpg")
    engine = create_async_engine(url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine


@fixture
async def async_session_factory(postgres_container, async_engine):
    yield async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@fixture
async def async_session(async_session_factory, async_engine):
    async with async_session_factory() as session:
        yield session
