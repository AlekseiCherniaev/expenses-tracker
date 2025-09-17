from datetime import datetime, timezone, timedelta
from uuid import uuid4, UUID

from psycopg import AsyncConnection
from pytest_asyncio import fixture
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer

from expenses_tracker.application.dto.budget import (
    BudgetUpdateDTO,
    BudgetCreateDTO,
    BudgetDTO,
)
from expenses_tracker.application.dto.category import (
    CategoryDTO,
    CategoryCreateDTO,
    CategoryUpdateDTO,
)
from expenses_tracker.application.dto.expense import (
    ExpenseUpdateDTO,
    ExpenseCreateDTO,
    ExpenseDTO,
)
from expenses_tracker.application.dto.user import UserDTO, UserUpdateDTO, UserCreateDTO
from expenses_tracker.core.constants import BudgetPeriod
from expenses_tracker.domain.entities.budget import Budget
from expenses_tracker.domain.entities.category import Category
from expenses_tracker.domain.entities.expense import Expense
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
async def create_test_user(unit_of_work):
    user = User(
        username="testuser", email="test@example.com", hashed_password="hashed_password"
    )
    async with unit_of_work as uow:
        created_user = await uow.user_repository.create(user)
        return created_user
    return None


@fixture
def unique_category_entity_with_times(
    random_uuid, unique_user_entity, create_test_user
):
    before_create = datetime.now(timezone.utc)
    category = Category(
        name=f"category_{random_uuid.hex[:6]}",
        user_id=create_test_user.id,
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
def unique_category_create_dto(create_test_user, random_uuid):
    return CategoryCreateDTO(
        user_id=create_test_user.id,
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


@fixture
def unique_expense_entity_with_times(
    random_uuid, create_test_user, create_test_category
):
    before_create = datetime.now(timezone.utc)
    expense = Expense(
        amount=150.75,
        date=datetime.now(),
        user_id=create_test_user.id,
        category_id=create_test_category.id,
        description="Test expense description",
    )
    after_create = datetime.now(timezone.utc)
    return expense, before_create, after_create


@fixture
def unique_expense_entity(unique_expense_entity_with_times):
    expense, _, _ = unique_expense_entity_with_times
    return expense


@fixture
def unique_expense_dto(unique_expense_entity):
    return ExpenseDTO(
        id=unique_expense_entity.id,
        amount=unique_expense_entity.amount,
        date=unique_expense_entity.date,
        user_id=unique_expense_entity.user_id,
        category_id=unique_expense_entity.category_id,
        description=unique_expense_entity.description,
        created_at=unique_expense_entity.created_at,
        updated_at=unique_expense_entity.updated_at,
    )


@fixture
def unique_expense_create_dto(
    create_test_user, create_test_category, unique_expense_entity
):
    return ExpenseCreateDTO(
        amount=unique_expense_entity.amount,
        date=unique_expense_entity.date,
        user_id=create_test_user.id,
        category_id=create_test_category.id,
        description=unique_expense_entity.description,
    )


@fixture
def unique_expense_update_dto(unique_expense_entity):
    return ExpenseUpdateDTO(
        id=unique_expense_entity.id,
        amount=300.25,
        date=datetime.now(),
        category_id=unique_expense_entity.category_id,
        description="Updated expense description",
    )


@fixture
async def create_test_category(unit_of_work, create_test_user):
    category = Category(
        name="TestCategory",
        user_id=create_test_user.id,
        color="blue",
        description="Test category for expenses",
    )
    async with unit_of_work as uow:
        created_category = await uow.category_repository.create(category)
        return created_category
    return None


@fixture
def unique_budget_entity_with_times(
    random_uuid, create_test_user, create_test_category
):
    before_create = datetime.now(timezone.utc)
    budget = Budget(
        amount=1000.0,
        period=BudgetPeriod.MONTHLY,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        user_id=create_test_user.id,
        category_id=create_test_category.id,
    )
    after_create = datetime.now(timezone.utc)
    return budget, before_create, after_create


@fixture
def unique_budget_entity(unique_budget_entity_with_times):
    budget, _, _ = unique_budget_entity_with_times
    return budget


@fixture
def unique_budget_dto(unique_budget_entity):
    return BudgetDTO(
        id=unique_budget_entity.id,
        amount=unique_budget_entity.amount,
        period=unique_budget_entity.period,
        start_date=unique_budget_entity.start_date,
        end_date=unique_budget_entity.end_date,
        user_id=unique_budget_entity.user_id,
        category_id=unique_budget_entity.category_id,
        created_at=unique_budget_entity.created_at,
        updated_at=unique_budget_entity.updated_at,
    )


@fixture
def unique_budget_create_dto(create_test_user, create_test_category):
    return BudgetCreateDTO(
        amount=1500.0,
        period=BudgetPeriod.WEEKLY,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=7),
        user_id=create_test_user.id,
        category_id=create_test_category.id,
    )


@fixture
def unique_budget_update_dto(unique_budget_entity):
    return BudgetUpdateDTO(
        id=unique_budget_entity.id,
        amount=2000.0,
        period=BudgetPeriod.MONTHLY,
        start_date=datetime.now() + timedelta(days=1),
        end_date=datetime.now() + timedelta(days=8),
        category_id=unique_budget_entity.category_id,
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
