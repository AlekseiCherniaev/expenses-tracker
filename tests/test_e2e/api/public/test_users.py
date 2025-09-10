from datetime import datetime
from uuid import UUID, uuid4

from pytest_asyncio import fixture

from expenses_tracker.infrastructure.api.schemas.user import (
    UserCreateRequest,
    UserUpdateRequest,
)


@fixture
def test_user_data():
    return {
        "id": UUID("a050493d-ed7a-4316-8f2a-77a2edc0a0c2"),
        "username": "test_username",
        "email": "test_email@test.com",
        "password": "password123",
        "is_active": False,
    }


@fixture
def unique_user_create_request(test_user_data):
    uid = uuid4().hex[:6]
    return UserCreateRequest(
        username=f"user_{uid}",
        password="password123",
        email=f"user_{uid}@test.com",
    )


@fixture
def user_update_request(test_user_data):
    return UserUpdateRequest(
        id=test_user_data["id"],
        password="new_password",
        email="new_email@test.com",
        is_active=True,
    )


class TestPublicUsersApi:
    async def test_health(self, async_client):
        response = await async_client.get("/internal/health")

        assert response.status_code == 200
        assert response.json() == {"status": "OK"}

    async def test_docs(self, async_client):
        response = await async_client.get("/internal/docs")

        assert response.status_code == 200

    async def _create_user(
        self, async_client, user_create_request
    ) -> (dict, datetime, datetime):
        before_create = datetime.now()
        response = await async_client.post(
            "/users/create", json=user_create_request.model_dump()
        )
        after_create = datetime.now()

        assert response.status_code == 200
        return response.json(), before_create, after_create

    async def test_create_user_success(self, async_client, unique_user_create_request):
        user, before_create, after_create = await self._create_user(
            async_client, unique_user_create_request
        )

        assert UUID(user["id"])
        assert user["username"] == unique_user_create_request.username
        assert user["email"] == unique_user_create_request.email
        assert user["is_active"] is False
        assert (
            before_create
            <= datetime.fromisoformat(user["created_at"])
            <= datetime.fromisoformat(user["updated_at"])
            <= after_create
        )

    async def test_create_user_conflicts(
        self, async_client, unique_user_create_request
    ):
        # create first user
        await self._create_user(async_client, unique_user_create_request)
        # conflict by email
        request_conflict_email = unique_user_create_request.model_copy(
            update={"username": "other_username"}
        )
        response = await async_client.post(
            "/users/create", json=request_conflict_email.model_dump()
        )

        assert response.status_code == 409
        assert "User with email" in response.json()["detail"]

        # conflict by username
        request_conflict_username = unique_user_create_request.model_copy(
            update={"email": "other@test.com"}
        )
        response = await async_client.post(
            "/users/create", json=request_conflict_username.model_dump()
        )

        assert response.status_code == 409
        assert "User with username" in response.json()["detail"]

    async def test_get_user_success(
        self, async_client, test_user_data, unique_user_create_request
    ):
        user, before_create, after_create = await self._create_user(
            async_client, unique_user_create_request
        )
        user_created_id = user["id"]
        response = await async_client.get(f"/users/get/{user_created_id}")
        user_get = response.json()

        assert response.status_code == 200
        assert user_get["id"] == user_created_id
        assert user_get["username"] == unique_user_create_request.username
        assert user_get["email"] == unique_user_create_request.email
        assert user_get["is_active"] == test_user_data["is_active"]
        assert (
            before_create
            <= datetime.fromisoformat(user["created_at"])
            <= datetime.fromisoformat(user["updated_at"])
            <= after_create
        )

    async def test_get_user_not_found(self, async_client):
        response = await async_client.get(f"/users/get/{uuid4()}")

        assert response.status_code == 404
        assert response.json()["detail"].startswith("User with id")

    async def test_get_all_users(self, async_client, test_user_data):
        # TODO
        assert True

    async def test_update_user_success(
        self,
        async_client,
        test_user_data,
        unique_user_create_request,
        user_update_request,
    ):
        user, before_create, after_create = await self._create_user(
            async_client, unique_user_create_request
        )
        user_created_id = user["id"]
        user_update_request.id = user_created_id
        before_update = datetime.now()
        response = await async_client.put(
            "/users/update", json=user_update_request.model_dump()
        )
        after_update = datetime.now()
        user = response.json()

        assert response.status_code == 200
        assert user["id"] == user_created_id
        assert user["username"] == unique_user_create_request.username
        assert user["email"] == user_update_request.email
        assert user["is_active"] == user_update_request.is_active
        assert (
            before_create <= datetime.fromisoformat(user["created_at"]) <= after_create
        )
        assert (
            before_update <= datetime.fromisoformat(user["updated_at"]) <= after_update
        )

    async def test_delete_user_success(
        self, async_client, test_user_data, unique_user_create_request
    ):
        user, _, _ = await self._create_user(async_client, unique_user_create_request)
        user_created_id = user["id"]
        response = await async_client.delete(f"/users/delete/{user_created_id}")

        assert response.status_code == 200
        assert response.json() is None
