from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from pytest_asyncio import fixture

from expenses_tracker.application.dto.user import UserDTO, UserCreateDTO, UserUpdateDTO
from expenses_tracker.application.interfaces.cache_service import ICacheService
from expenses_tracker.application.interfaces.email_service import IEmailService
from expenses_tracker.application.interfaces.password_hasher import IPasswordHasher
from expenses_tracker.application.interfaces.token_service import ITokenService
from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.repositories.budget import IBudgetRepository
from expenses_tracker.domain.repositories.category import ICategoryRepository
from expenses_tracker.domain.repositories.expense import IExpenseRepository
from expenses_tracker.domain.repositories.uow import IUnitOfWork
from expenses_tracker.domain.repositories.user import IUserRepository


@fixture
def user_entity():
    return User(
        id=uuid4(),
        username="test",
        email="test@test.com",
        hashed_password="hashed_password",
    )


@fixture
def user_dto(user_entity):
    return UserDTO(
        id=user_entity.id,
        username=user_entity.username,
        email=user_entity.email,
        email_verified=user_entity.email_verified,
        created_at=user_entity.created_at,
        updated_at=user_entity.updated_at,
        last_refresh_jti=user_entity.last_refresh_jti,
    )


@fixture
def user_create_dto(user_entity):
    return UserCreateDTO(
        username=user_entity.username, email=user_entity.email, password="new_password"
    )


@fixture
def user_update_dto(user_entity):
    return UserUpdateDTO(id=user_entity.id, email="new_email", password="new_password")


@fixture
def mock_unit_of_work():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    mock_uow.__aenter__ = AsyncMock()
    mock_uow.__aexit__ = AsyncMock(return_value=False)
    mock_user_repo = AsyncMock(spec=IUserRepository)
    mock_budget_repo = AsyncMock(spec=IBudgetRepository)
    mock_category_repo = AsyncMock(spec=ICategoryRepository)
    mock_expense_repo = AsyncMock(spec=IExpenseRepository)
    mock_uow.__aenter__.return_value.expense_repository = mock_expense_repo
    mock_uow.__aenter__.return_value.category_repository = mock_category_repo
    mock_uow.__aenter__.return_value.budget_repository = mock_budget_repo
    mock_uow.__aenter__.return_value.user_repository = mock_user_repo
    return mock_uow


@fixture
def mock_password_hasher(user_entity):
    mock_hasher = Mock(spec=IPasswordHasher)
    mock_hasher.hash.return_value = user_entity.hashed_password
    mock_hasher.verify.return_value = True
    return mock_hasher


@fixture
def cache_service_mock():
    mock = AsyncMock(spec=ICacheService)
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock()
    return mock


@fixture
def mock_token_service():
    mock_service = Mock(spec=ITokenService)
    mock_service.create_token.return_value = "test_token"
    mock_service.decode_token.return_value = Mock(sub=str(uuid4()))
    return mock_service


@fixture
def mock_email_service():
    mock_service = Mock(spec=IEmailService)
    mock_service.send_verification_email.return_value = None
    return mock_service
