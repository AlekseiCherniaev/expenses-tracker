from datetime import datetime, timezone
from uuid import UUID

from pytest_asyncio import fixture

from expenses_tracker.domain.entities.user import User
from expenses_tracker.infrastructure.database.repositories.user.dummy_user_repo import (
    DummyUserRepository,
)
from expenses_tracker.infrastructure.database.repositories.user.psycopg_user_repo import (
    PsycopgUserRepository,
)
from expenses_tracker.infrastructure.database.repositories.user.sqlalchemy_user_repo import (
    SQLAlchemyUserRepository,
)


@fixture
def user_entity():
    return User(
        username="test",
        hashed_password="hashed_test",
        email="testemail@gmail.com",
        email_verified=True,
    )


@fixture(params=["dummy", "sqlalchemy", "psycopg"])
def repo(request, async_session, async_connection):
    match request.param:
        case "dummy":
            return DummyUserRepository()
        case "sqlalchemy":
            return SQLAlchemyUserRepository(session=async_session)
        case "psycopg":
            return PsycopgUserRepository(conn=async_connection)
        case _:
            raise ValueError(f"Unknown repo {request.param}")


class TestRepository:
    @fixture(autouse=True)
    def setup(self, repo):
        self.repo = repo

    async def _create_user(self, user_entity):
        return await self.repo.create(user_entity)

    async def test_get_by_id_success(self, user_entity):
        new_user = await self._create_user(user_entity)
        user = await self.repo.get_by_id(new_user.id)

        assert isinstance(user, User)
        assert user == user_entity

    async def test_get_by_id_not_found(self):
        user = await self.repo.get_by_id(UUID("00000000-0000-0000-0000-000000000000"))
        assert user is None

    async def test_get_by_username_success(self, user_entity):
        new_user = await self._create_user(user_entity)
        user = await self.repo.get_by_username(new_user.username)

        assert isinstance(user, User)
        assert user == user_entity

    async def test_get_by_email(self, user_entity):
        new_user = await self._create_user(user_entity)
        user = await self.repo.get_by_email(new_user.email)

        assert isinstance(user, User)
        assert user == user_entity

    async def test_get_all_success(self, user_entity):
        await self._create_user(user_entity)
        users = await self.repo.get_all()

        assert isinstance(users, list)
        assert len(users) == 1
        assert users[0] == user_entity

    async def test_create_success(self):
        username = "new_user"
        hashed_password = "hashed_password123"
        user = await self.repo.create(
            User(username=username, hashed_password=hashed_password)
        )

        assert isinstance(user, User)
        assert user.username == username
        assert user.email is None
        assert user.hashed_password == hashed_password
        assert user.email_verified is False

    async def test_update_success(self, user_entity):
        new_email = "new_email@example.com"
        user_entity.email = new_email
        user_entity.updated_at = datetime.now(timezone.utc)
        user = await self.repo.update(user_entity)

        assert isinstance(user, User)
        assert user.email == new_email

    async def test_delete_success(self, user_entity):
        created_user = await self._create_user(user_entity)
        await self.repo.delete(created_user)

        assert await self.repo.get_by_id(created_user.id) is None
