from psycopg import AsyncConnection
from pytest_asyncio import fixture
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer

from expenses_tracker.infrastructure.database.models import Base


@fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres


@fixture(scope="session")
def postgres_container_sync_url(postgres_container):
    # For psycopg
    return postgres_container.get_connection_url().replace("+psycopg2", "")


@fixture(scope="session")
def postgres_container_async_url(postgres_container):
    # For sqlalchemy-asyncpg
    return postgres_container.get_connection_url().replace("psycopg2", "asyncpg")


@fixture
async def async_connection(postgres_container_sync_url):
    conn = await AsyncConnection.connect(postgres_container_sync_url)
    yield conn
    await conn.close()


@fixture
async def async_engine(postgres_container_async_url):
    engine = create_async_engine(postgres_container_async_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@fixture
def async_session_factory(async_engine):
    yield async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


@fixture
async def async_session(async_session_factory):
    async with async_session_factory() as session:
        yield session
