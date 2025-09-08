from datetime import datetime

from pytest_asyncio import fixture

from expenses_tracker.domain.entities.user import User
from expenses_tracker.infrastructure.database.repositories.dummy_repo import (
    DummyUserRepository,
    create_dummy_user,
)


@fixture
def dummy_user():
    return create_dummy_user()


@fixture
async def dummy_repo(dummy_user):
    return DummyUserRepository(initial_user=dummy_user)


class TestDummyUserRepository:
    async def test_get_by_id(self, dummy_repo, dummy_user):
        user = await dummy_repo.get_by_id(dummy_user.id)

        assert isinstance(user, User)
        assert user == dummy_user

    async def test_get_by_username(self, dummy_repo, dummy_user):
        user = await dummy_repo.get_by_username(dummy_user.username)

        assert isinstance(user, User)
        assert user == dummy_user

    async def test_get_by_email(self, dummy_repo, dummy_user):
        user = await dummy_repo.get_by_email(dummy_user.email)

        assert isinstance(user, User)
        assert user == dummy_user

    async def test_get_all(self, dummy_repo, dummy_user):
        users = await dummy_repo.get_all()

        assert isinstance(users, list)
        assert len(users) == 1
        assert users[0] == dummy_user

    async def test_create(self, dummy_repo):
        username = "new_user"
        hashed_password = "hashed_password123"

        user = await dummy_repo.create(
            User(username=username, hashed_password=hashed_password)
        )

        assert isinstance(user, User)
        assert user.username == username
        assert user.email is None
        assert user.hashed_password == hashed_password
        assert user.is_active is False

    async def test_update(self, dummy_repo, dummy_user):
        new_email = "new_email@example.com"

        user = await dummy_repo.update(
            User(
                id=dummy_user.id,
                email=new_email,
                username=dummy_user.username,
                is_active=dummy_user.is_active,
                hashed_password=dummy_user.hashed_password,
                created_at=dummy_user.created_at,
                updated_at=datetime.now(),
            )
        )

        assert isinstance(user, User)
        assert user.email == new_email
        assert user.id == dummy_user.id
        assert user.username == dummy_user.username
        assert user.is_active == dummy_user.is_active
        assert user.hashed_password == dummy_user.hashed_password

    async def test_delete(self, dummy_repo, dummy_user):
        await dummy_repo.delete(dummy_user.id)

        assert dummy_repo.users == {}
