from expenses_tracker.infrastructure.security.password_hasher import (
    BcryptPasswordHasher,
)


class TestBcryptPasswordHasher:
    def test_password_hasher_hash_and_verify(self):
        hasher = BcryptPasswordHasher()
        raw_password = "super-secret"

        hashed = hasher.hash(raw_password)

        assert hashed != raw_password
        assert hasher.verify(raw_password, hashed) is True
        assert hasher.verify("wrong-password", hashed) is False
