from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.infrastructure.database.db import get_db_engines
from expenses_tracker.infrastructure.database.repositories.sqlalchemy_uow import (
    SqlAlchemyUnitOfWork,
)
from expenses_tracker.infrastructure.security.password_hasher import (
    BcryptPasswordHasher,
)


async def get_user_use_cases() -> UserUseCases:
    unit_of_work = SqlAlchemyUnitOfWork(
        session_factory=get_db_engines().async_session_factory
    )
    password_hasher = BcryptPasswordHasher()
    return UserUseCases(unit_of_work=unit_of_work, password_hasher=password_hasher)
