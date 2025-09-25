from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import status

from expenses_tracker.infrastructure.api.endpoints.public.auth import TokenResponse
from expenses_tracker.infrastructure.api.endpoints.public.category import (
    CategoryCreateRequest,
)


class TestCategoryApi:
    async def _register_user(self, async_client, user_create_request):
        register_response = await async_client.post(
            "/api/auth/register", json=user_create_request.model_dump()
        )
        token_response = TokenResponse(**register_response.json())
        return token_response.access_token

    async def _get_auth_headers(self, access_token):
        return {"Authorization": f"Bearer {access_token}"}

    async def _create_category_via_api(
        self, async_client, access_token, category_create_request: CategoryCreateRequest
    ) -> (dict, datetime, datetime):
        headers = await self._get_auth_headers(access_token)
        before_create = datetime.now(timezone.utc)
        response = await async_client.post(
            "/api/categories/create",
            json=category_create_request.model_dump(),
            headers=headers,
        )
        after_create = datetime.now(timezone.utc)

        assert response.status_code == status.HTTP_200_OK
        return response.json(), before_create, after_create

    async def test_get_category_success(
        self, async_client, unique_user_create_request, unique_category_create_request
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)
        (
            category_create,
            before_create,
            after_create,
        ) = await self._create_category_via_api(
            async_client, access_token, unique_category_create_request
        )
        category_id = category_create["id"]
        response = await async_client.get(
            f"/api/categories/get/{category_id}", headers=headers
        )
        category_get = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert category_get["id"] == category_id
        assert category_get["name"] == unique_category_create_request.name
        assert category_get["description"] == unique_category_create_request.description
        assert category_get["is_default"] == unique_category_create_request.is_default
        assert category_get["color"] == unique_category_create_request.color
        assert (
            before_create
            <= datetime.fromisoformat(category_get["created_at"])
            <= datetime.fromisoformat(category_get["updated_at"])
            <= after_create
        )

    async def test_get_category_unauthorized(self, async_client):
        response = await async_client.get(f"/api/categories/get/{uuid4()}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_category_not_found(
        self, async_client, unique_user_create_request
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)
        response = await async_client.get(
            f"/api/categories/get/{uuid4()}", headers=headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Category with id" in response.json()["detail"]

    async def test_get_categories_by_user_success(
        self, async_client, unique_user_create_request, unique_category_create_request
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)
        (
            category_create,
            before_create,
            after_create,
        ) = await self._create_category_via_api(
            async_client, access_token, unique_category_create_request
        )
        response = await async_client.get(
            "/api/categories/get-by-user", headers=headers
        )
        categories_get = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(categories_get, list)
        assert len(categories_get) == 1

        created_category = categories_get[0]
        assert created_category["id"] == category_create["id"]
        assert created_category["name"] == unique_category_create_request.name
        assert (
            created_category["description"]
            == unique_category_create_request.description
        )
        assert (
            before_create
            <= datetime.fromisoformat(created_category["created_at"])
            <= datetime.fromisoformat(created_category["updated_at"])
            <= after_create
        )

    async def test_get_categories_by_user_empty(
        self, async_client, unique_user_create_request
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)

        response = await async_client.get(
            "/api/categories/get-by-user", headers=headers
        )
        categories_get = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(categories_get, list)
        assert len(categories_get) == 0

    async def test_get_categories_by_user_unauthorized(self, async_client):
        response = await async_client.get("/api/categories/get-by-user")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_category_success(
        self, async_client, unique_user_create_request, unique_category_create_request
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        (
            category_create,
            before_create,
            after_create,
        ) = await self._create_category_via_api(
            async_client, access_token, unique_category_create_request
        )

        assert UUID(category_create["id"])
        assert category_create["name"] == unique_category_create_request.name
        assert (
            category_create["description"] == unique_category_create_request.description
        )
        assert (
            category_create["is_default"] == unique_category_create_request.is_default
        )
        assert category_create["color"] == unique_category_create_request.color
        assert (
            before_create
            <= datetime.fromisoformat(category_create["created_at"])
            <= datetime.fromisoformat(category_create["updated_at"])
            <= after_create
        )

    async def test_create_category_unauthorized(
        self, async_client, unique_category_create_request
    ):
        response = await async_client.post(
            "/api/categories/create", json=unique_category_create_request.model_dump()
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_category_success(
        self,
        async_client,
        unique_user_create_request,
        unique_category_create_request,
        category_update_request,
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)
        (
            category_create,
            before_create,
            after_create,
        ) = await self._create_category_via_api(
            async_client, access_token, unique_category_create_request
        )
        category_update_request.id = category_create["id"]
        before_update = datetime.now(timezone.utc)
        response = await async_client.put(
            "/api/categories/update",
            json=category_update_request.model_dump(),
            headers=headers,
        )
        after_update = datetime.now(timezone.utc)
        category_update = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert category_update["id"] == category_create["id"]
        assert category_update["name"] == category_update_request.name
        assert category_update["description"] == category_update_request.description
        assert category_update["is_default"] == category_update_request.is_default
        assert category_update["color"] == category_update_request.color
        assert (
            before_create
            <= datetime.fromisoformat(category_update["created_at"])
            <= after_create
        )
        assert (
            before_update
            <= datetime.fromisoformat(category_update["updated_at"])
            <= after_update
        )

    async def test_update_category_unauthorized(
        self, async_client, category_update_request
    ):
        category_update_request.id = str(uuid4())
        response = await async_client.put(
            "/api/categories/update", json=category_update_request.model_dump()
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_category_not_found(
        self, async_client, unique_user_create_request, category_update_request
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)

        category_update_request.id = str(uuid4())
        response = await async_client.put(
            "/api/categories/update",
            json=category_update_request.model_dump(),
            headers=headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Category with id" in response.json()["detail"]

    async def test_delete_category_success(
        self, async_client, unique_user_create_request, unique_category_create_request
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)
        category_create, _, _ = await self._create_category_via_api(
            async_client, access_token, unique_category_create_request
        )
        category_id = category_create["id"]
        response = await async_client.delete(
            f"/api/categories/delete/{category_id}", headers=headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        response_get = await async_client.get(
            f"/api/categories/get/{category_id}", headers=headers
        )
        assert response_get.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_category_unauthorized(self, async_client):
        response = await async_client.delete(f"/api/categories/delete/{uuid4()}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_category_not_found(
        self, async_client, unique_user_create_request
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)

        response = await async_client.delete(
            f"/api/categories/delete/{uuid4()}", headers=headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Category with id" in response.json()["detail"]

    async def test_full_category_lifecycle(
        self,
        async_client,
        unique_user_create_request,
        unique_category_create_request,
        category_update_request,
    ):
        access_token = await self._register_user(
            async_client, unique_user_create_request
        )
        headers = await self._get_auth_headers(access_token)
        category_create, _, _ = await self._create_category_via_api(
            async_client, access_token, unique_category_create_request
        )
        get_response = await async_client.get(
            f"/api/categories/get/{category_create['id']}", headers=headers
        )
        assert get_response.status_code == status.HTTP_200_OK

        category_update_request.id = category_create["id"]
        update_response = await async_client.put(
            "/api/categories/update",
            json=category_update_request.model_dump(),
            headers=headers,
        )
        assert update_response.status_code == status.HTTP_200_OK

        delete_response = await async_client.delete(
            f"/api/categories/delete/{category_create['id']}", headers=headers
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        final_get_response = await async_client.get(
            f"/api/categories/get/{category_create['id']}", headers=headers
        )
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND
