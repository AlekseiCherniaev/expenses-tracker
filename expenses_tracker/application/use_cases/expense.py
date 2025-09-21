from datetime import datetime, timezone
from uuid import UUID

import structlog

from expenses_tracker.application.dto.expense import (
    ExpenseDTO,
    ExpenseCreateDTO,
    ExpenseUpdateDTO,
)
from expenses_tracker.domain.entities.expense import Expense
from expenses_tracker.domain.exceptions.expense import ExpenseNotFound
from expenses_tracker.domain.repositories.uow import IUnitOfWork

logger = structlog.get_logger(__name__)


class ExpenseUseCases:
    def __init__(self, unit_of_work: IUnitOfWork):
        self._unit_of_work = unit_of_work

    async def get_expense(self, expense_id: UUID) -> ExpenseDTO:
        async with self._unit_of_work as uow:
            expense = await uow.expense_repository.get_by_id(expense_id=expense_id)
            if not expense:
                raise ExpenseNotFound(f"Expense with id {expense_id} not found")
            logger.bind(expense=expense).debug("Retrieved expense from repo")
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
        assert False, "unreachable"

    async def get_expenses_by_user_id(self, user_id: UUID) -> list[ExpenseDTO]:
        async with self._unit_of_work as uow:
            expenses = await uow.expense_repository.get_all_by_user_id(user_id=user_id)
            logger.bind(expenses=expenses).debug("Retrieved expenses from repo")
            return [
                ExpenseDTO(
                    id=expense.id,
                    amount=expense.amount,
                    date=expense.date,
                    user_id=expense.user_id,
                    category_id=expense.category_id,
                    description=expense.description,
                    created_at=expense.created_at,
                    updated_at=expense.updated_at,
                )
                for expense in expenses
            ]
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
            return [
                ExpenseDTO(
                    id=expense.id,
                    amount=expense.amount,
                    date=expense.date,
                    user_id=expense.user_id,
                    category_id=expense.category_id,
                    description=expense.description,
                    created_at=expense.created_at,
                    updated_at=expense.updated_at,
                )
                for expense in expenses
            ]
        assert False, "unreachable"

    async def get_expenses_by_user_id_and_category_id(
        self, user_id: UUID, category_id: UUID
    ) -> list[ExpenseDTO]:
        async with self._unit_of_work as uow:
            expenses = await uow.expense_repository.get_by_user_id_and_category_id(
                user_id=user_id, category_id=category_id
            )
            logger.bind(expenses=expenses).debug(
                "Retrieved expenses by category from repo"
            )
            return [
                ExpenseDTO(
                    id=expense.id,
                    amount=expense.amount,
                    date=expense.date,
                    user_id=expense.user_id,
                    category_id=expense.category_id,
                    description=expense.description,
                    created_at=expense.created_at,
                    updated_at=expense.updated_at,
                )
                for expense in expenses
            ]
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
        assert False, "unreachable"

    async def delete_expense(self, expense_id: UUID) -> None:
        async with self._unit_of_work as uow:
            expense = await uow.expense_repository.get_by_id(expense_id=expense_id)
            if not expense:
                raise ExpenseNotFound(f"Expense with id {expense_id} not found")
            await uow.expense_repository.delete(expense=expense)
            logger.bind(expense=expense).debug("Deleted expense in repo")
            return None
        assert False, "unreachable"
