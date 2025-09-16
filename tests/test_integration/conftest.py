from datetime import datetime, timezone
from uuid import uuid4, UUID

from psycopg import AsyncConnection
from pytest_asyncio import fixture
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer

from expenses_tracker.application.dto.category import (
    CategoryDTO,
    CategoryCreateDTO,
    CategoryUpdateDTO,
)
from expenses_tracker.application.dto.user import UserDTO, UserUpdateDTO, UserCreateDTO
from expenses_tracker.domain.entities.category import Category
from expenses_tracker.domain.entities.user import User
from expenses_tracker.infrastructure.database.models import Base
from expenses_tracker.infrastructure.database.repositories.dummy_uow import (
    DummyUnitOfWork,
)
from expenses_tracker.infrastructure.database.repositories.psycopg_uow import (
    PsycopgUnitOfWork,
)
from expenses_tracker.infrastructure.database.repositories.sqlalchemy_uow import (
    SqlAlchemyUnitOfWork,
)
from expenses_tracker.infrastructure.security.bcrypt_password_hasher import (
    BcryptPasswordHasher,
)
from expenses_tracker.infrastructure.security.jwt_token_service import JWTTokenService


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


@fixture(autouse=True)
def random_uuid() -> UUID:
    return uuid4()


@fixture
def unique_user_create_dto(random_uuid):
    uid = random_uuid.hex[:6]
    return UserCreateDTO(
        username=f"user_{uid}",
        password="password123",
        email=f"user_{uid}@test.com",
    )


@fixture
def unique_user_entity_with_times(random_uuid) -> (User, datetime, datetime):
    before_create = datetime.now(timezone.utc)
    uid = random_uuid.hex[:6]
    user = User(
        username=f"user_{uid}",
        hashed_password="hashed_password123",
        email=f"user_{uid}@test.com",
    )
    after_create = datetime.now(timezone.utc)
    return user, before_create, after_create


@fixture
def unique_user_entity(unique_user_entity_with_times):
    user, _, _ = unique_user_entity_with_times
    return user


@fixture
def unique_user_dto(unique_user_entity):
    return UserDTO(
        id=unique_user_entity.id,
        username=unique_user_entity.username,
        email=unique_user_entity.email,
        is_active=unique_user_entity.is_active,
        created_at=unique_user_entity.created_at,
        updated_at=unique_user_entity.updated_at,
    )


@fixture
def unique_user_update_dto(unique_user_entity):
    return UserUpdateDTO(
        id=unique_user_entity.id,
        password="new_password",
        email="new_email@test.com",
        is_active=True,
    )


@fixture
def unique_category_entity_with_times(random_uuid, unique_user_entity):
    before_create = datetime.now(timezone.utc)
    category = Category(
        name=f"category_{random_uuid.hex[:6]}",
        user_id=unique_user_entity.id,
        color="red",
        description="Test category",
    )
    after_create = datetime.now(timezone.utc)
    return category, before_create, after_create


@fixture
def unique_category_entity(unique_category_entity_with_times):
    category, _, _ = unique_category_entity_with_times
    return category


@fixture
def unique_category_dto(unique_category_entity):
    return CategoryDTO(
        id=unique_category_entity.id,
        name=unique_category_entity.name,
        user_id=unique_category_entity.user_id,
        description=unique_category_entity.description,
        is_default=unique_category_entity.is_default,
        color=unique_category_entity.color,
        created_at=unique_category_entity.created_at,
        updated_at=unique_category_entity.updated_at,
    )


@fixture
def unique_category_create_dto(unique_user_entity, random_uuid):
    return CategoryCreateDTO(
        user_id=unique_user_entity.id,
        name=f"category_{random_uuid.hex[:6]}",
        description="New test category",
        is_default=False,
        color="blue",
    )


@fixture
def unique_category_update_dto(unique_category_entity):
    return CategoryUpdateDTO(
        id=unique_category_entity.id,
        name="updated_name",
        color="green",
        is_default=True,
        description="Updated description",
    )


@fixture(params=["bcrypt_hasher"])
def password_hasher(request):
    match request.param:
        case "bcrypt_hasher":
            return BcryptPasswordHasher()
        case _:
            raise ValueError(f"Unknown password_hasher {request.param}")


@fixture(params=["jwt_token_service"])
def token_service(request):
    match request.param:
        case "jwt_token_service":
            return JWTTokenService()
        case _:
            raise ValueError(f"Unknown token_service {request.param}")


@fixture(params=["dummy", "sqlalchemy", "psycopg"])
def unit_of_work(request, async_session_factory, postgres_container_sync_url):
    match request.param:
        case "dummy":
            return DummyUnitOfWork()
        case "sqlalchemy":
            return SqlAlchemyUnitOfWork(session_factory=async_session_factory)
        case "psycopg":
            return PsycopgUnitOfWork(dns=postgres_container_sync_url)
        case _:
            raise ValueError(f"Unknown repo {request.param}")
