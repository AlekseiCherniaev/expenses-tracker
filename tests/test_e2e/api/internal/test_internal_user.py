from datetime import datetime, timezone
from uuid import UUID, uuid4


class TestInternalUserApi:
    async def test_health(self, async_client):
        response = await async_client.get("/api/health")

        assert response.status_code == 200
        assert response.json() == {"status": "OK"}

    async def test_docs(self, async_client):
        response = await async_client.get("/api/internal/docs")

        assert response.status_code == 200

    async def _create_user(
        self, async_client, user_create_request
    ) -> (dict, datetime, datetime):
        before_create = datetime.now(timezone.utc)
        response = await async_client.post(
            "/api/internal/users/create", json=user_create_request.model_dump()
        )
        after_create = datetime.now(timezone.utc)

        assert response.status_code == 200
        return response.json(), before_create, after_create

    async def test_create_user_success(self, async_client, unique_user_create_request):
        user_create, before_create, after_create = await self._create_user(
            async_client, unique_user_create_request
        )

        assert UUID(user_create["id"])
        assert user_create["username"] == unique_user_create_request.username
        assert user_create["email"] == unique_user_create_request.email
        assert user_create["email_verified"] is False
        assert (
            before_create
            <= datetime.fromisoformat(user_create["created_at"])
            <= datetime.fromisoformat(user_create["updated_at"])
            <= after_create
        )

    async def test_create_user_conflicts(
        self, async_client, unique_user_create_request
    ):
        await self._create_user(async_client, unique_user_create_request)

        request_conflict_username = unique_user_create_request.model_copy(
            update={"email": "other@test.com"}
        )
        response = await async_client.post(
            "/api/internal/users/create", json=request_conflict_username.model_dump()
        )

        assert response.status_code == 400
        assert "User with username" in response.json()["detail"]

    async def test_get_user_success(self, async_client, unique_user_create_request):
        user_create, before_create, after_create = await self._create_user(
            async_client, unique_user_create_request
        )
        user_created_id = user_create["id"]
        response = await async_client.get(f"/api/internal/users/get/{user_created_id}")
        user_get = response.json()

        assert response.status_code == 200
        assert user_get["id"] == user_created_id
        assert user_get["username"] == unique_user_create_request.username
        assert user_get["email"] == unique_user_create_request.email
        assert user_get["email_verified"] is False
        assert (
            before_create
            <= datetime.fromisoformat(user_get["created_at"])
            <= datetime.fromisoformat(user_get["updated_at"])
            <= after_create
        )

    async def test_get_user_not_found(self, async_client):
        response = await async_client.get(f"/api/internal/users/get/{uuid4()}")

        assert response.status_code == 404
        assert response.json()["detail"].startswith("User with id")

    async def test_get_all_users_success(
        self, async_client, unique_user_create_request
    ):
        user_create, before_create, after_create = await self._create_user(
            async_client, unique_user_create_request
        )
        response = await async_client.get("/api/internal/users/get-all")
        users_get = response.json()

        assert response.status_code == 200
        assert isinstance(users_get, list)
        created_user = next(
            user for user in users_get if user["id"] == user_create["id"]
        )
        assert created_user is not None
        assert created_user["id"] == user_create["id"]
        assert created_user["username"] == unique_user_create_request.username
        assert created_user["email"] == unique_user_create_request.email
        assert created_user["email_verified"] is False
        assert (
            before_create
            <= datetime.fromisoformat(created_user["created_at"])
            <= datetime.fromisoformat(created_user["updated_at"])
            <= after_create
        )

    async def test_update_user_success(
        self,
        async_client,
        unique_user_create_request,
        user_update_request,
    ):
        user_create, before_create, after_create = await self._create_user(
            async_client, unique_user_create_request
        )
        user_update_request.id = user_create["id"]
        before_update = datetime.now(timezone.utc)
        response = await async_client.put(
            "/api/internal/users/update", json=user_update_request.model_dump()
        )
        after_update = datetime.now(timezone.utc)
        user_update = response.json()

        assert response.status_code == 200
        assert user_update["id"] == user_create["id"]
        assert user_update["username"] == unique_user_create_request.username
        assert user_update["email"] == user_update_request.email
        assert (
            before_create
            <= datetime.fromisoformat(user_update["created_at"])
            <= after_create
        )
        assert (
            before_update
            <= datetime.fromisoformat(user_update["updated_at"])
            <= after_update
        )

    async def test_delete_user_success(self, async_client, unique_user_create_request):
        user_create, _, _ = await self._create_user(
            async_client, unique_user_create_request
        )
        user_created_id = user_create["id"]
        response = await async_client.delete(
            f"/api/internal/users/delete/{user_created_id}"
        )

        assert response.status_code == 204
