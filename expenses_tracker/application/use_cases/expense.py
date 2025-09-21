from datetime import datetime, timezone
from uuid import UUID

import structlog

from expenses_tracker.application.dto.expense import (
    ExpenseDTO,
    ExpenseCreateDTO,
    ExpenseUpdateDTO,
)
from expenses_tracker.application.interfaces.cache_service import ICacheService
from expenses_tracker.core.settings import get_settings
from expenses_tracker.domain.entities.expense import Expense
from expenses_tracker.domain.exceptions.expense import ExpenseNotFound
from expenses_tracker.domain.repositories.uow import IUnitOfWork

logger = structlog.get_logger(__name__)


class ExpenseUseCases:
    def __init__(
        self,
        unit_of_work: IUnitOfWork,
        cache_service: ICacheService[ExpenseDTO | list[ExpenseDTO]],
    ):
        self._unit_of_work = unit_of_work
        self._cache_service = cache_service

    @staticmethod
    def _to_dto(expense: Expense) -> ExpenseDTO:
        return ExpenseDTO(
            id=expense.id,
            amount=expense.amount,
            date=expense.date,
            user_id=expense.user_id,
            category_id=expense.category_id,
            description=expense.description,
            created_at=expense.created_at,
            updated_at=expense.updated_at,
        )

    @staticmethod
    def _expense_cache_key(expense_id: UUID) -> str:
        return f"expense:{expense_id}"

    @staticmethod
    def _user_expenses_cache_key(user_id: UUID) -> str:
        return f"expenses:user:{user_id}"

    @staticmethod
    def _user_category_expenses_cache_key(user_id: UUID, category_id: UUID) -> str:
        return f"expenses:user:{user_id}:category:{category_id}"

    async def get_expense(self, expense_id: UUID) -> ExpenseDTO:
        cache_key = self._expense_cache_key(expense_id)
        cached_expense = await self._cache_service.get(
            key=cache_key, serializer=ExpenseDTO
        )
        if cached_expense:
            logger.bind(expense_id=expense_id).debug("Retrieved expense from cache")
            return cached_expense  # type: ignore

        async with self._unit_of_work as uow:
            expense = await uow.expense_repository.get_by_id(expense_id=expense_id)
            if not expense:
                raise ExpenseNotFound(f"Expense with id {expense_id} not found")

            dto = self._to_dto(expense)
            await self._cache_service.set(
                key=cache_key, value=dto, ttl=get_settings().expense_dto_ttl_seconds
            )
            logger.bind(expense_id=expense_id).debug(
                "Retrieved expense from repo and cached"
            )
            return dto
        assert False, "unreachable"

    async def get_expenses_by_user_id(self, user_id: UUID) -> list[ExpenseDTO]:
        cache_key = self._user_expenses_cache_key(user_id)
        cached_expenses = await self._cache_service.get(
            key=cache_key, serializer=list[ExpenseDTO]
        )
        if cached_expenses:
            logger.bind(user_id=user_id, count=len(cached_expenses)).debug(  # type: ignore
                "Retrieved budgets from cache"
            )
            return cached_expenses  # type: ignore

        async with self._unit_of_work as uow:
            expenses = await uow.expense_repository.get_all_by_user_id(user_id=user_id)
            dtos = [self._to_dto(e) for e in expenses]
            await self._cache_service.set(
                key=cache_key, value=dtos, ttl=get_settings().expenses_list_ttl_seconds
            )
            logger.bind(user_id=user_id, count=len(dtos)).debug(
                "Retrieved expenses by user from repo and cached"
            )
            return dtos
        assert False, "unreachable"

    async def get_expenses_by_user_id_and_date_range(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[ExpenseDTO]:
        async with self._unit_of_work as uow:
            expenses = await uow.expense_repository.get_by_user_id_and_date_range(
                user_id=user_id, start_date=start_date, end_date=end_date
            )
            logger.bind(expenses=expenses).debug(
                "Retrieved expenses by date range from repo"
            )
            return [self._to_dto(e) for e in expenses]
        assert False, "unreachable"

    async def get_expenses_by_user_id_and_category_id(
        self, user_id: UUID, category_id: UUID
    ) -> list[ExpenseDTO]:
        cache_key = self._user_category_expenses_cache_key(user_id, category_id)
        cached_expenses = await self._cache_service.get(
            key=cache_key, serializer=list[ExpenseDTO]
        )
        if cached_expenses:
            logger.bind(user_id=user_id, count=len(cached_expenses)).debug(  # type: ignore
                "Retrieved budgets from cache"
            )
            return cached_expenses  # type: ignore

        async with self._unit_of_work as uow:
            expenses = await uow.expense_repository.get_by_user_id_and_category_id(
                user_id=user_id, category_id=category_id
            )
            dtos = [self._to_dto(e) for e in expenses]
            await self._cache_service.set(
                key=cache_key, value=dtos, ttl=get_settings().expenses_list_ttl_seconds
            )
            logger.bind(user_id=user_id, count=len(dtos)).debug(
                "Retrieved expenses by user and category from repo and cached"
            )
            return dtos
        assert False, "unreachable"

    async def create_expense(self, expense_data: ExpenseCreateDTO) -> ExpenseDTO:
        async with self._unit_of_work as uow:
            new_expense = Expense(
                amount=expense_data.amount,
                date=expense_data.date,
                user_id=expense_data.user_id,
                category_id=expense_data.category_id,
                description=expense_data.description,
            )
            expense = await uow.expense_repository.create(expense=new_expense)
            logger.bind(expense=expense).debug("Created expense in repo")
            dto = self._to_dto(expense)

            await self._cache_service.set(
                key=self._expense_cache_key(dto.id),
                value=dto,
                ttl=get_settings().expense_dto_ttl_seconds,
            )
            # invalidate user expenses cache
            await self._cache_service.delete(
                key=self._user_expenses_cache_key(expense.user_id)
            )
            await self._cache_service.delete(
                key=self._user_category_expenses_cache_key(
                    expense.user_id, expense.category_id
                )
            )
            return dto
        assert False, "unreachable"

    async def update_expense(self, expense_data: ExpenseUpdateDTO) -> ExpenseDTO:
        async with self._unit_of_work as uow:
            expense = await uow.expense_repository.get_by_id(expense_id=expense_data.id)
            if not expense:
                raise ExpenseNotFound(f"Expense with id {expense_data.id} not found")

            if expense_data.amount is not None:
                expense.amount = expense_data.amount
            if expense_data.date is not None:
                expense.date = expense_data.date
            if expense_data.category_id is not None:
                expense.category_id = expense_data.category_id
            if expense_data.description is not None:
                expense.description = expense_data.description

            expense.updated_at = datetime.now(timezone.utc)
            updated_expense = await uow.expense_repository.update(expense=expense)
            logger.bind(updated_expense=updated_expense).debug(
                "Updated expense in repo"
            )

            dto = self._to_dto(updated_expense)
            await self._cache_service.set(
                key=self._expense_cache_key(dto.id),
                value=dto,
                ttl=get_settings().expense_dto_ttl_seconds,
            )
            # invalidate user expenses cache
            await self._cache_service.delete(
                key=self._user_expenses_cache_key(expense.user_id)
            )
            await self._cache_service.delete(
                key=self._user_category_expenses_cache_key(
                    expense.user_id, expense.category_id
                )
            )
            return dto
        assert False, "unreachable"

    async def delete_expense(self, expense_id: UUID) -> None:
        async with self._unit_of_work as uow:
            expense = await uow.expense_repository.get_by_id(expense_id=expense_id)
            if not expense:
                raise ExpenseNotFound(f"Expense with id {expense_id} not found")
            await uow.expense_repository.delete(expense=expense)
            logger.bind(expense=expense).debug("Deleted expense in repo")

            await self._cache_service.delete(key=self._expense_cache_key(expense_id))
            await self._cache_service.delete(
                key=self._user_expenses_cache_key(expense.user_id)
            )
            await self._cache_service.delete(
                key=self._user_category_expenses_cache_key(
                    expense.user_id, expense.category_id
                )
            )
            return None
        assert False, "unreachable"
