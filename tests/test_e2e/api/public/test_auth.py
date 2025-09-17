from starlette import status

from expenses_tracker.infrastructure.api.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
)
from expenses_tracker.infrastructure.api.schemas.user import (
    InternalUserCreateRequest,
)


class TestAuthApi:
    async def _register_user(self, async_client, user_create_request):
        response = await async_client.post(
            "/auth/register", json=user_create_request.model_dump()
        )
        assert response.status_code == status.HTTP_200_OK
        return TokenResponse(**response.json())

    async def test_register_success(self, async_client, unique_user_create_request):
        response = await async_client.post(
            "/auth/register", json=unique_user_create_request.model_dump()
        )

        assert response.status_code == status.HTTP_200_OK
        token_response = TokenResponse(**response.json())

        assert token_response.access_token is not None
        assert token_response.refresh_token is not None
        assert token_response.token_type == "bearer"

        login_response = await async_client.post(
            "/auth/login",
            json=LoginRequest(
                username=unique_user_create_request.username,
                password=unique_user_create_request.password,
            ).model_dump(),
        )
        assert login_response.status_code == status.HTTP_200_OK

    async def test_register_user_already_exists(
        self, async_client, unique_user_create_request
    ):
        response1 = await async_client.post(
            "/auth/register", json=unique_user_create_request.model_dump()
        )
        assert response1.status_code == status.HTTP_200_OK

        response2 = await async_client.post(
            "/auth/register", json=unique_user_create_request.model_dump()
        )

        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response2.json()["detail"].lower()

    async def test_register_conflict_username(
        self, async_client, unique_user_create_request
    ):
        await self._register_user(async_client, unique_user_create_request)

        conflict_request = InternalUserCreateRequest(
            username=unique_user_create_request.username,
            password="different_password",
            email="different@test.com",
        )

        response = await async_client.post(
            "/auth/register", json=conflict_request.model_dump()
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.json()["detail"].lower()

    async def test_register_conflict_email(
        self, async_client, unique_user_create_request
    ):
        await self._register_user(async_client, unique_user_create_request)

        conflict_request = InternalUserCreateRequest(
            username="different_username",
            password="different_password",
            email=unique_user_create_request.email,
        )

        response = await async_client.post(
            "/auth/register", json=conflict_request.model_dump()
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()["detail"].lower()

    async def test_login_success(
        self, async_client, unique_user_create_request, login_request
    ):
        register_tokens = await self._register_user(
            async_client, unique_user_create_request
        )

        response = await async_client.post(
            "/auth/login", json=login_request.model_dump()
        )

        assert response.status_code == status.HTTP_200_OK
        login_tokens = TokenResponse(**response.json())

        assert login_tokens.access_token is not None
        assert login_tokens.refresh_token is not None
        assert login_tokens.token_type == "bearer"
        assert login_tokens.access_token != register_tokens.access_token
        assert login_tokens.refresh_token != register_tokens.refresh_token

    async def test_login_user_not_found(self, async_client):
        login_request = LoginRequest(
            username="nonexistent_user", password="password123"
        )

        response = await async_client.post(
            "/auth/login", json=login_request.model_dump()
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    async def test_login_invalid_password(
        self, async_client, unique_user_create_request
    ):
        await self._register_user(async_client, unique_user_create_request)

        invalid_login = LoginRequest(
            username=unique_user_create_request.username, password="wrong_password"
        )

        response = await async_client.post(
            "/auth/login", json=invalid_login.model_dump()
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            "invalid" in response.json()["detail"].lower()
            or "credentials" in response.json()["detail"].lower()
        )

    async def test_refresh_success(self, async_client, unique_user_create_request):
        register_tokens = await self._register_user(
            async_client, unique_user_create_request
        )
        refresh_request = RefreshRequest(refresh_token=register_tokens.refresh_token)
        response = await async_client.post(
            "/auth/refresh", json=refresh_request.model_dump()
        )

        assert response.status_code == status.HTTP_200_OK

        refresh_tokens = TokenResponse(**response.json())

        assert refresh_tokens.access_token is not None
        assert refresh_tokens.refresh_token is not None
        assert refresh_tokens.token_type == "bearer"
        assert refresh_tokens.access_token != register_tokens.access_token
        assert refresh_tokens.refresh_token != register_tokens.refresh_token

    async def test_refresh_user_not_found(
        self, async_client, unique_user_create_request
    ):
        refresh_request = RefreshRequest(refresh_token="invalid_token_format")

        response = await async_client.post(
            "/auth/refresh", json=refresh_request.model_dump()
        )

        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        ]

    async def test_refresh_invalid_token(self, async_client):
        refresh_request = RefreshRequest(refresh_token="clearly_invalid_token_string")

        response = await async_client.post(
            "/auth/refresh", json=refresh_request.model_dump()
        )

        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        ]
        assert (
            "token" in response.json()["detail"].lower()
            or "invalid" in response.json()["detail"].lower()
        )

    async def test_full_auth_flow(self, async_client, unique_user_create_request):
        register_response = await async_client.post(
            "/auth/register", json=unique_user_create_request.model_dump()
        )

        assert register_response.status_code == status.HTTP_200_OK

        register_tokens = TokenResponse(**register_response.json())
        login_response = await async_client.post(
            "/auth/login",
            json=LoginRequest(
                username=unique_user_create_request.username,
                password=unique_user_create_request.password,
            ).model_dump(),
        )

        assert login_response.status_code == status.HTTP_200_OK

        login_tokens = TokenResponse(**login_response.json())
        refresh_response = await async_client.post(
            "/auth/refresh",
            json=RefreshRequest(refresh_token=login_tokens.refresh_token).model_dump(),
        )

        assert refresh_response.status_code == status.HTTP_200_OK

        refresh_tokens = TokenResponse(**refresh_response.json())

        assert all(
            tokens.access_token is not None
            for tokens in [register_tokens, login_tokens, refresh_tokens]
        )
        assert all(
            tokens.refresh_token is not None
            for tokens in [register_tokens, login_tokens, refresh_tokens]
        )
        assert register_tokens.access_token != login_tokens.access_token
        assert login_tokens.access_token != refresh_tokens.access_token
        assert register_tokens.refresh_token != login_tokens.refresh_token
        assert login_tokens.refresh_token != refresh_tokens.refresh_token
