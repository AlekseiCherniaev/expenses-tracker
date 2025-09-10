from datetime import datetime
from uuid import UUID

from pytest_asyncio import fixture

from expenses_tracker.domain.entities.user import User
from expenses_tracker.infrastructure.database.repositories.dummy_repo import (
    DummyUserRepository,
)


@fixture
def dummy_user():
    return User(
        username="test",
        hashed_password="hashed_test",
        email="testemail@gmail.com",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


class TestDummyUserRepository:
    @fixture(autouse=True)
    def setup(self):
        self.dummy_repo = DummyUserRepository()

    async def _create_user(self, user_entity):
        return await self.dummy_repo.create(user_entity)

    async def test_get_by_id_success(self, dummy_user):
        new_user = await self._create_user(dummy_user)
        user = await self.dummy_repo.get_by_id(new_user.id)

        assert isinstance(user, User)
        assert user == dummy_user

    async def test_get_by_id_not_found(self):
        user = await self.dummy_repo.get_by_id(
            UUID("00000000-0000-0000-0000-000000000000")
        )
        assert user is None

    async def test_get_by_username_success(self, dummy_user):
        new_user = await self._create_user(dummy_user)
        user = await self.dummy_repo.get_by_username(new_user.username)

        assert isinstance(user, User)
        assert user == dummy_user

    async def test_get_by_email(self, dummy_user):
        new_user = await self._create_user(dummy_user)
        user = await self.dummy_repo.get_by_email(new_user.email)

        assert isinstance(user, User)
        assert user == dummy_user

    async def test_get_all_success(self, dummy_user):
        await self._create_user(dummy_user)
        users = await self.dummy_repo.get_all()

        assert isinstance(users, list)
        assert len(users) == 1
        assert users[0] == dummy_user

    async def test_create_success(self):
        username = "new_user"
        hashed_password = "hashed_password123"
        user = await self.dummy_repo.create(
            User(username=username, hashed_password=hashed_password)
        )

        assert isinstance(user, User)
        assert user.username == username
        assert user.email is None
        assert user.hashed_password == hashed_password
        assert user.is_active is False
        assert user.id in self.dummy_repo.users

    async def test_update_success(self, dummy_user):
        new_email = "new_email@example.com"
        dummy_user.email = new_email
        dummy_user.updated_at = datetime.now()
        user = await self.dummy_repo.update(dummy_user)

        assert isinstance(user, User)
        assert user.email == new_email
        assert self.dummy_repo.users[dummy_user.id].email == new_email

    async def test_delete_success(self, dummy_user):
        created_user = await self._create_user(dummy_user)
        await self.dummy_repo.delete(created_user.id)

        assert await self.dummy_repo.get_by_id(created_user.id) is None
        assert created_user.id not in self.dummy_repo.users
