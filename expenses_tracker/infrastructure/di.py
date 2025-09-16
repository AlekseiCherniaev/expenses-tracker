from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from expenses_tracker.application.use_cases.auth import AuthUserUseCases
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.domain.repositories.uow import IUnitOfWork
from expenses_tracker.infrastructure.database.repositories.psycopg_uow import (
    PsycopgUnitOfWork,
)
from expenses_tracker.infrastructure.database.repositories.sqlalchemy_uow import (
    SqlAlchemyUnitOfWork,
)
from expenses_tracker.infrastructure.security.bcrypt_password_hasher import (
    BcryptPasswordHasher,
)
from expenses_tracker.infrastructure.security.jwt_token_service import JWTTokenService


async def get_sqlalchemy_uow(request: Request) -> SqlAlchemyUnitOfWork:
    async_engine = request.app.state.sqlalchemy_engine
    session_factory = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    return SqlAlchemyUnitOfWork(session_factory=session_factory)


async def get_psycopg_uow(request: Request) -> PsycopgUnitOfWork:
    dsn = request.app.state.psycopg_dsn
    return PsycopgUnitOfWork(dns=dsn)


async def get_user_use_cases(
    uow: IUnitOfWork = Depends(get_psycopg_uow),
) -> UserUseCases:
    return UserUseCases(unit_of_work=uow, password_hasher=BcryptPasswordHasher())


async def get_auth_user_use_cases(
    uow: IUnitOfWork = Depends(get_psycopg_uow),
) -> AuthUserUseCases:
    return AuthUserUseCases(
        unit_of_work=uow,
        password_hasher=BcryptPasswordHasher(),
        token_service=JWTTokenService(),
    )
