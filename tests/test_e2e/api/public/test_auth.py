from starlette import status

from expenses_tracker.infrastructure.api.schemas.auth import LoginRequest
from expenses_tracker.infrastructure.api.schemas.user import InternalUserCreateRequest


class TestAuthApi:
    async def _register_user(self, async_client, user_create_request):
        response = await async_client.post(
            "/api/auth/register", json=user_create_request.model_dump()
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "refresh_token" not in data
        assert "refresh_token" in response.cookies
        assert "csrf_token" in response.cookies
        return response

    async def test_register_success(self, async_client, unique_user_create_request):
        response = await async_client.post(
            "/api/auth/register", json=unique_user_create_request.model_dump()
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "refresh_token" not in data
        assert "refresh_token" in response.cookies
        assert "csrf_token" in response.cookies

        login_response = await async_client.post(
            "/api/auth/login",
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
            "/api/auth/register", json=unique_user_create_request.model_dump()
        )
        assert response1.status_code == status.HTTP_200_OK

        response2 = await async_client.post(
            "/api/auth/register", json=unique_user_create_request.model_dump()
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
            "/api/auth/register", json=conflict_request.model_dump()
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
            "/api/auth/register", json=conflict_request.model_dump()
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()["detail"].lower()

    async def test_login_success(
        self, async_client, unique_user_create_request, login_request
    ):
        await self._register_user(async_client, unique_user_create_request)
        response = await async_client.post(
            "/api/auth/login", json=login_request.model_dump()
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "refresh_token" not in data
        assert "refresh_token" in response.cookies
        assert "csrf_token" in response.cookies

    async def test_login_user_not_found(self, async_client):
        login_request = LoginRequest(
            username="nonexistent_user", password="password123"
        )
        response = await async_client.post(
            "/api/auth/login", json=login_request.model_dump()
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
            "/api/auth/login", json=invalid_login.model_dump()
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            "invalid" in response.json()["detail"].lower()
            or "credentials" in response.json()["detail"].lower()
        )

    async def test_refresh_success(self, async_client, unique_user_create_request):
        register_response = await self._register_user(
            async_client, unique_user_create_request
        )
        csrf_token = register_response.cookies["csrf_token"]
        response = await async_client.post(
            "/api/auth/refresh",
            headers={"X-CSRF-Token": csrf_token},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "refresh_token" not in data
        assert "refresh_token" in response.cookies
        assert "csrf_token" in response.cookies

    async def test_refresh_invalid_token(self, async_client):
        response = await async_client.post(
            "/api/auth/refresh", headers={"X-CSRF-Token": "fake"}
        )
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    async def test_full_auth_flow(self, async_client, unique_user_create_request):
        register_response = await async_client.post(
            "/api/auth/register", json=unique_user_create_request.model_dump()
        )
        assert register_response.status_code == status.HTTP_200_OK

        login_response = await async_client.post(
            "/api/auth/login",
            json=LoginRequest(
                username=unique_user_create_request.username,
                password=unique_user_create_request.password,
            ).model_dump(),
        )
        assert login_response.status_code == status.HTTP_200_OK
        csrf_token = login_response.cookies["csrf_token"]

        refresh_response = await async_client.post(
            "/api/auth/refresh",
            headers={"X-CSRF-Token": csrf_token},
        )
        assert refresh_response.status_code == status.HTTP_200_OK
