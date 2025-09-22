from fastapi import status

from expenses_tracker.infrastructure.api.schemas.auth import LoginRequest, TokenResponse
from expenses_tracker.infrastructure.api.schemas.user import UserResponse


class TestUserApi:
    async def _register_user(self, async_client, user_create_request):
        register_response = await async_client.post(
            "/auth/register", json=user_create_request.model_dump()
        )
        token_response = TokenResponse(**register_response.json())
        return token_response.access_token

    async def _get_auth_headers(self, access_token):
        return {"Authorization": f"Bearer {access_token}"}

    async def test_get_current_user_success(
        self, async_client, unique_user_create_request
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)
        response = await async_client.get("/users/me", headers=headers)
        user_response = UserResponse(**response.json())

        assert response.status_code == status.HTTP_200_OK
        assert user_response.username == unique_user_create_request.username
        assert user_response.email == unique_user_create_request.email
        assert user_response.is_active is False

    async def test_get_current_user_unauthorized(self, async_client):
        response = await async_client.get("/users/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_current_user_invalid_token(self, async_client):
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get("/users/me", headers=headers)

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_400_BAD_REQUEST,
        ]

    async def test_update_current_user_success(
        self, async_client, unique_user_create_request, user_update_request
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)
        user_update_request.id = str(user_update_request.id)
        response = await async_client.put(
            "/users/update", json=user_update_request.model_dump(), headers=headers
        )
        user_response = UserResponse(**response.json())

        assert response.status_code == status.HTTP_200_OK
        assert user_response.email == user_update_request.email
        assert user_response.is_active == user_update_request.is_active
        assert user_response.username == unique_user_create_request.username

        get_response = await async_client.get("/users/me", headers=headers)
        updated_user = UserResponse(**get_response.json())

        assert updated_user.email == user_update_request.email
        assert updated_user.is_active == user_update_request.is_active

    async def test_update_current_user_unauthorized(
        self, async_client, user_update_request
    ):
        user_update_request.id = str(user_update_request.id)
        response = await async_client.put(
            "/users/update", json=user_update_request.model_dump()
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_current_user_success(
        self, async_client, unique_user_create_request
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)
        response = await async_client.delete("/users/delete", headers=headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        get_response = await async_client.get("/users/me", headers=headers)

        assert get_response.status_code == status.HTTP_404_NOT_FOUND

        login_response = await async_client.post(
            "/auth/login",
            json=LoginRequest(
                username=unique_user_create_request.username,
                password=unique_user_create_request.password,
            ).model_dump(),
        )

        assert login_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_current_user_unauthorized(self, async_client):
        response = await async_client.delete("/users/delete")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_full_user_lifecycle(
        self, async_client, unique_user_create_request, user_update_request
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)
        get_response = await async_client.get("/users/me", headers=headers)
        original_user = UserResponse(**get_response.json())

        assert get_response.status_code == status.HTTP_200_OK

        user_update_request.id = str(user_update_request.id)
        update_response = await async_client.put(
            "/users/update", json=user_update_request.model_dump(), headers=headers
        )
        updated_user = UserResponse(**update_response.json())

        assert update_response.status_code == status.HTTP_200_OK
        assert updated_user.email == user_update_request.email
        assert updated_user.is_active == user_update_request.is_active
        assert updated_user.username == original_user.username

        delete_response = await async_client.delete("/users/delete", headers=headers)

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        final_get_response = await async_client.get("/users/me", headers=headers)

        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_user_caching(
        self, async_client, unique_user_create_request, redis_client
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)
        response = await async_client.get("/users/me", headers=headers)
        user_response = UserResponse(**response.json())
        cache_key = f"user:{user_response.id}"
        cached = await redis_client.get(cache_key)

        assert cached is not None, "User must be cached in Redis after first get"

        await redis_client.delete(cache_key)
        await async_client.get("/users/me", headers=headers)
        cached2 = await redis_client.get(cache_key)

        assert cached2 is not None, "User must be cached again after cache miss"
