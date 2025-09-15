from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.core.settings import get_settings
from expenses_tracker.infrastructure.database.repositories.psycopg_uow import (
    PsycopgUnitOfWork,
)
from expenses_tracker.infrastructure.security.password_hasher import (
    BcryptPasswordHasher,
)


async def get_user_use_cases() -> UserUseCases:
    unit_of_work = PsycopgUnitOfWork(dns=get_settings().sync_postgres_url)
    password_hasher = BcryptPasswordHasher()
    return UserUseCases(unit_of_work=unit_of_work, password_hasher=password_hasher)
