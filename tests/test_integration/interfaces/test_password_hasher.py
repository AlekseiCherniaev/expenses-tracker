from pytest_asyncio import fixture

from expenses_tracker.infrastructure.security.password_hasher import (
    BcryptPasswordHasher,
)


@fixture(params=["bcrypt_hasher"])
def password_hasher(request):
    match request.param:
        case "bcrypt_hasher":
            return BcryptPasswordHasher()
        case _:
            raise ValueError(f"Unknown password_hasher {request.param}")


class TestPasswordHasher:
    def test_password_hasher_hash_and_verify(self, password_hasher):
        hasher = password_hasher
        raw_password = "super-secret"
        hashed = hasher.hash(raw_password)

        assert hashed != raw_password
        assert hasher.verify(raw_password, hashed) is True
        assert hasher.verify("wrong-password", hashed) is False
