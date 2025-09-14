from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.infrastructure.database.db import async_session_factory
from expenses_tracker.infrastructure.database.repositories.sqlalchemy_uow import (
    SqlAlchemyUnitOfWork,
)
from expenses_tracker.infrastructure.security.password_hasher import (
    BcryptPasswordHasher,
)


async def get_user_use_cases() -> UserUseCases:
    unit_of_work = SqlAlchemyUnitOfWork(session_factory=async_session_factory)
    password_hasher = BcryptPasswordHasher()
    return UserUseCases(unit_of_work=unit_of_work, password_hasher=password_hasher)
