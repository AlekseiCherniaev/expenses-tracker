from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.infrastructure.database.repositories.dummy_uow import (
    DummyUnitOfWork,
)
from expenses_tracker.infrastructure.security.password_hasher import (
    BcryptPasswordHasher,
)


async def get_user_use_cases() -> UserUseCases:
    unit_of_work = DummyUnitOfWork()
    password_hasher = BcryptPasswordHasher()
    return UserUseCases(unit_of_work=unit_of_work, password_hasher=password_hasher)
