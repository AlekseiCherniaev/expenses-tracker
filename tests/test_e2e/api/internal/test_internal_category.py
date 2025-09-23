from datetime import datetime, timezone
from uuid import UUID, uuid4

from expenses_tracker.infrastructure.api.endpoints.internal.category import (
    InternalCategoryCreateRequest,
    InternalCategoryUpdateRequest,
)


class TestInternalCategoryApi:
    async def _create_user(self, async_client, unique_user_create_request) -> UUID:
        response = await async_client.post(
            "/internal/users/create", json=unique_user_create_request.model_dump()
        )

        assert response.status_code == 200
        return response.json()["id"]

    async def _create_category(
        self,
        async_client,
        category_create_request: InternalCategoryCreateRequest,
        user_id,
    ) -> (dict, datetime, datetime):
        before_create = datetime.now(timezone.utc)
        category_create_request.user_id = user_id
        response = await async_client.post(
            "/internal/categories/create", json=category_create_request.model_dump()
        )
        after_create = datetime.now(timezone.utc)

        assert response.status_code == 200
        return response.json(), before_create, after_create

    async def test_create_category_success(
        self,
        async_client,
        unique_internal_category_create_request,
        unique_user_create_request,
    ):
        user_id = await self._create_user(async_client, unique_user_create_request)
        category_create, before_create, after_create = await self._create_category(
            async_client, unique_internal_category_create_request, user_id
        )

        assert UUID(category_create["id"])
        assert category_create["user_id"] == str(user_id)
        assert category_create["name"] == unique_internal_category_create_request.name
        assert (
            category_create["description"]
            == unique_internal_category_create_request.description
        )
        assert (
            category_create["is_default"]
            == unique_internal_category_create_request.is_default
        )
        assert category_create["color"] == unique_internal_category_create_request.color
        assert (
            before_create
            <= datetime.fromisoformat(category_create["created_at"])
            <= datetime.fromisoformat(category_create["updated_at"])
            <= after_create
        )

    async def test_get_category_success(
        self,
        async_client,
        unique_internal_category_create_request,
        unique_user_create_request,
    ):
        user_id = await self._create_user(async_client, unique_user_create_request)
        category_create, before_create, after_create = await self._create_category(
            async_client, unique_internal_category_create_request, user_id
        )

        category_id = category_create["id"]
        response = await async_client.get(f"/internal/categories/get/{category_id}")
        category_get = response.json()

        assert response.status_code == 200
        assert category_get["id"] == category_id
        assert category_get["user_id"] == str(user_id)
        assert category_get["name"] == unique_internal_category_create_request.name
        assert (
            category_get["description"]
            == unique_internal_category_create_request.description
        )
        assert (
            category_get["is_default"]
            == unique_internal_category_create_request.is_default
        )
        assert category_get["color"] == unique_internal_category_create_request.color
        assert (
            before_create
            <= datetime.fromisoformat(category_get["created_at"])
            <= datetime.fromisoformat(category_get["updated_at"])
            <= after_create
        )

    async def test_get_category_not_found(self, async_client):
        response = await async_client.get(f"/internal/categories/get/{uuid4()}")

        assert response.status_code == 404
        assert "Category with id" in response.json()["detail"]

    async def test_get_categories_by_user_success(
        self,
        async_client,
        unique_internal_category_create_request,
        unique_user_create_request,
    ):
        user_id = await self._create_user(async_client, unique_user_create_request)
        category_create, before_create, after_create = await self._create_category(
            async_client, unique_internal_category_create_request, user_id
        )

        response = await async_client.get(f"/internal/categories/get-by-user/{user_id}")
        categories_get = response.json()

        assert response.status_code == 200
        assert isinstance(categories_get, list)
        assert len(categories_get) == 1

        created_category = categories_get[0]
        assert created_category["id"] == category_create["id"]
        assert created_category["user_id"] == str(user_id)
        assert created_category["name"] == unique_internal_category_create_request.name
        assert (
            created_category["description"]
            == unique_internal_category_create_request.description
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
        user_id = await self._create_user(async_client, unique_user_create_request)

        response = await async_client.get(f"/internal/categories/get-by-user/{user_id}")
        categories_get = response.json()

        assert response.status_code == 200
        assert isinstance(categories_get, list)
        assert len(categories_get) == 0

    async def test_get_categories_by_user_not_found(self, async_client):
        response = await async_client.get(f"/internal/categories/get-by-user/{uuid4()}")

        assert response.status_code == 200
        assert response.json() == []

    async def test_update_category_success(
        self,
        async_client,
        unique_internal_category_create_request,
        category_update_request,
        unique_user_create_request,
    ):
        user_id = await self._create_user(async_client, unique_user_create_request)
        category_create, before_create, after_create = await self._create_category(
            async_client, unique_internal_category_create_request, user_id
        )
        before_update = datetime.now(timezone.utc)
        category_update_request.id = category_create["id"]
        response = await async_client.put(
            "/internal/categories/update", json=category_update_request.model_dump()
        )
        after_update = datetime.now(timezone.utc)
        category_update = response.json()

        assert response.status_code == 200
        assert category_update["id"] == category_create["id"]
        assert category_update["user_id"] == str(user_id)
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

    async def test_update_category_not_found(
        self, async_client, category_update_request
    ):
        category_update_request.id = str(uuid4())
        response = await async_client.put(
            "/internal/categories/update", json=category_update_request.model_dump()
        )

        assert response.status_code == 404
        assert "Category with id" in response.json()["detail"]

    async def test_delete_category_success(
        self,
        async_client,
        unique_internal_category_create_request,
        unique_user_create_request,
    ):
        user_id = await self._create_user(async_client, unique_user_create_request)
        category_create, _, _ = await self._create_category(
            async_client, unique_internal_category_create_request, user_id
        )
        category_id = category_create["id"]
        response = await async_client.delete(
            f"/internal/categories/delete/{category_id}"
        )

        assert response.status_code == 204

        response_get = await async_client.get(f"/internal/categories/get/{category_id}")
        assert response_get.status_code == 404

    async def test_delete_category_not_found(self, async_client):
        response = await async_client.delete(f"/internal/categories/delete/{uuid4()}")

        assert response.status_code == 404
        assert "Category with id" in response.json()["detail"]

    async def test_partial_update_category(
        self,
        async_client,
        unique_internal_category_create_request,
        unique_user_create_request,
    ):
        user_id = await self._create_user(async_client, unique_user_create_request)
        category_create, _, _ = await self._create_category(
            async_client, unique_internal_category_create_request, user_id
        )

        partial_update = InternalCategoryUpdateRequest(
            id=category_create["id"],
            name="Updated Name Only",
            description=None,
            is_default=None,
            color=None,
        )
        partial_update.id = category_create["id"]
        response = await async_client.put(
            "/internal/categories/update", json=partial_update.model_dump()
        )
        category_update = response.json()

        assert response.status_code == 200
        assert category_update["name"] == "Updated Name Only"
        assert (
            category_update["description"]
            == unique_internal_category_create_request.description
        )
        assert (
            category_update["is_default"]
            == unique_internal_category_create_request.is_default
        )
        assert category_update["color"] == unique_internal_category_create_request.color
