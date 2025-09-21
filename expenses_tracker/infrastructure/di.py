from typing import Any

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from expenses_tracker.application.dto.budget import BudgetDTO
from expenses_tracker.application.dto.category import CategoryDTO
from expenses_tracker.application.dto.expense import ExpenseDTO
from expenses_tracker.application.dto.user import UserDTO
from expenses_tracker.application.interfaces.cache_service import ICacheService
from expenses_tracker.application.interfaces.password_hasher import IPasswordHasher
from expenses_tracker.application.interfaces.token_service import ITokenService
from expenses_tracker.application.use_cases.auth import AuthUserUseCases
from expenses_tracker.application.use_cases.budget import BudgetUseCases
from expenses_tracker.application.use_cases.category import CategoryUseCases
from expenses_tracker.application.use_cases.expense import ExpenseUseCases
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.domain.repositories.uow import IUnitOfWork
from expenses_tracker.infrastructure.database.repositories.psycopg_uow import (
    PsycopgUnitOfWork,
)
from expenses_tracker.infrastructure.database.repositories.sqlalchemy_uow import (
    SqlAlchemyUnitOfWork,
)


def get_token_service(request: Request) -> ITokenService:
    return request.app.state.token_service  # type: ignore


def get_redis_service(request: Request) -> ICacheService[Any]:
    return request.app.state.redis_service  # type: ignore


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
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
    cache_service: ICacheService[UserDTO] = Depends(get_redis_service),
) -> UserUseCases:
    return UserUseCases(
        unit_of_work=uow,
        password_hasher=password_hasher,
        cache_service=cache_service,
    )


async def get_category_use_cases(
    uow: IUnitOfWork = Depends(get_psycopg_uow),
    cache_service: ICacheService[CategoryDTO | list[CategoryDTO]] = Depends(
        get_redis_service
    ),
) -> CategoryUseCases:
    return CategoryUseCases(unit_of_work=uow, cache_service=cache_service)


async def get_expense_use_cases(
    uow: IUnitOfWork = Depends(get_psycopg_uow),
    cache_service: ICacheService[ExpenseDTO | list[ExpenseDTO]] = Depends(
        get_redis_service
    ),
) -> ExpenseUseCases:
    return ExpenseUseCases(unit_of_work=uow, cache_service=cache_service)


async def get_budget_use_cases(
    uow: IUnitOfWork = Depends(get_psycopg_uow),
    cache_service: ICacheService[BudgetDTO | list[BudgetDTO]] = Depends(
        get_redis_service
    ),
) -> BudgetUseCases:
    return BudgetUseCases(unit_of_work=uow, cache_service=cache_service)


async def get_auth_user_use_cases(
    uow: IUnitOfWork = Depends(get_psycopg_uow),
    token_service: ITokenService = Depends(get_token_service),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
) -> AuthUserUseCases:
    return AuthUserUseCases(
        unit_of_work=uow,
        password_hasher=password_hasher,
        token_service=token_service,
    )
