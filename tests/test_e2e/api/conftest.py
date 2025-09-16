from uuid import UUID, uuid4

from pytest_asyncio import fixture

from expenses_tracker.infrastructure.api.schemas.auth import (
    RefreshRequest,
    TokenResponse,
    LoginRequest,
)
from expenses_tracker.infrastructure.api.schemas.category import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
)
from expenses_tracker.infrastructure.api.schemas.internal_category import (
    InternalCategoryCreateRequest,
)
from expenses_tracker.infrastructure.api.schemas.internal_user import (
    InternalUserCreateRequest,
    InternalUserUpdateRequest,
)


@fixture(autouse=True)
def random_uuid() -> UUID:
    return uuid4()


@fixture
def unique_user_create_request(random_uuid):
    uid = random_uuid.hex[:6]
    return InternalUserCreateRequest(
        username=f"user_{uid}",
        password="password123",
        email=f"user_{uid}@test.com",
    )


@fixture
def user_update_request(random_uuid):
    return InternalUserUpdateRequest(
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


@fixture
def unique_category_create_request(random_uuid):
    uid = random_uuid.hex[:6]
    return CategoryCreateRequest(
        name=f"category_{uid}",
        description=f"Test category {uid}",
        is_default=False,
        color=f"#{uid}",
    )


@fixture
def unique_internal_category_create_request(random_uuid):
    uid = random_uuid.hex[:6]
    return InternalCategoryCreateRequest(
        name=f"category_{uid}",
        user_id=random_uuid,
        description=f"Test category {uid}",
        is_default=False,
        color=f"#{uid}",
    )


@fixture
def category_update_request(random_uuid):
    uid = random_uuid.hex[:6]
    return CategoryUpdateRequest(
        id=random_uuid,
        name=f"updated_category_{uid}",
        description=f"Updated description {uid}",
        is_default=True,
        color=f"#updated{uid}",
    )
