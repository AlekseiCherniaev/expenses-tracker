from datetime import datetime
from uuid import UUID

from expenses_tracker.domain.entities.user import User


class TestUser:
    def test_user_creation_success(self):
        username = "testuser"
        hashed_password = "hashedpassword"

        user = User(username, hashed_password)
        assert user.username == username
        assert user.hashed_password == hashed_password
        assert isinstance(user.id, UUID)
        assert user.is_active is False
        assert user.email is None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
