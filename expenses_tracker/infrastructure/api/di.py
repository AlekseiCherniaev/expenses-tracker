from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.infrastructure.database.repositories.dummy_repo import (
    DummyUserRepository,
)
from expenses_tracker.infrastructure.security.password_hasher import (
    BcryptPasswordHasher,
)


async def get_user_use_cases() -> UserUseCases:
    repo = DummyUserRepository()
    password_hasher = BcryptPasswordHasher()
    return UserUseCases(user_repository=repo, password_hasher=password_hasher)
