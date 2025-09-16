from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from expenses_tracker.application.interfaces.password_hasher import IPasswordHasher
from expenses_tracker.application.interfaces.token_service import ITokenService
from expenses_tracker.application.use_cases.auth import AuthUserUseCases
from expenses_tracker.application.use_cases.categories import CategoryUseCases
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


def get_token_service(request: Request) -> ITokenService:
    return request.app.state.token_service  # type: ignore


def get_password_hasher(request: Request) -> IPasswordHasher:
    return request.app.state.password_hasher  # type: ignore


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


async def get_category_use_cases(
    uow: IUnitOfWork = Depends(get_psycopg_uow),
) -> CategoryUseCases:
    return CategoryUseCases(unit_of_work=uow)


async def get_auth_user_use_cases(
    uow: IUnitOfWork = Depends(get_psycopg_uow),
    token_service: JWTTokenService = Depends(get_token_service),
    password_hasher: BcryptPasswordHasher = Depends(get_password_hasher),
) -> AuthUserUseCases:
    return AuthUserUseCases(
        unit_of_work=uow,
        password_hasher=password_hasher,
        token_service=token_service,
    )
