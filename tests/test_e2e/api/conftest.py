from uuid import UUID, uuid4

from pytest_asyncio import fixture

from expenses_tracker.infrastructure.api.schemas.auth import (
    RefreshRequest,
    TokenResponse,
    LoginRequest,
)
from expenses_tracker.infrastructure.api.schemas.internal_user import (
    UserCreateRequest,
    UserUpdateRequest,
)


@fixture(autouse=True)
def random_uuid() -> UUID:
    return uuid4()


@fixture
def unique_user_create_request(random_uuid):
    uid = random_uuid.hex[:6]
    return UserCreateRequest(
        username=f"user_{uid}",
        password="password123",
        email=f"user_{uid}@test.com",
    )


@fixture
def user_update_request(random_uuid):
    return UserUpdateRequest(
        id=random_uuid,
        password="new_password",
        email="new_email@test.com",
        is_active=True,
    )


@fixture
def login_request(unique_user_create_request):
    return LoginRequest(
        username=unique_user_create_request.username,
        password=unique_user_create_request.password,
    )


@fixture
def refresh_request(random_uuid):
    return RefreshRequest(refresh_token="test_refresh_token")


@fixture
def token_response():
    return TokenResponse(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        token_type="bearer",
    )
