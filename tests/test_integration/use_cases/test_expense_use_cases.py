from datetime import datetime, timezone

import pytest
from pytest import fixture

from expenses_tracker.application.dto.expense import (
    ExpenseDTO,
    ExpenseUpdateDTO,
)
from expenses_tracker.application.use_cases.expense import ExpenseUseCases
from expenses_tracker.domain.entities.expense import Expense
from expenses_tracker.domain.exceptions.expense import ExpenseNotFound


class TestExpenseUseCases:
    @fixture(autouse=True)
    def setup(self, unit_of_work):
        self.expense_use_cases = ExpenseUseCases(unit_of_work=unit_of_work)
        self.unit_of_work = unit_of_work

    async def _create_expense(self, expense_entity: Expense) -> Expense:
        async with self.unit_of_work as uow:
            return await uow.expense_repository.create(expense_entity)

    async def test_get_expense_success(self, unique_expense_entity, unique_expense_dto):
        new_expense = await self._create_expense(unique_expense_entity)
        expense = await self.expense_use_cases.get_expense(expense_id=new_expense.id)

        assert isinstance(expense, ExpenseDTO)
        assert expense == unique_expense_dto

    async def test_get_expense_not_found(self, random_uuid):
        with pytest.raises(ExpenseNotFound):
            await self.expense_use_cases.get_expense(expense_id=random_uuid)

    async def test_get_expenses_by_user_id_success(
        self, unique_expense_entity, unique_expense_dto
    ):
        await self._create_expense(unique_expense_entity)
        expenses = await self.expense_use_cases.get_expenses_by_user_id(
            user_id=unique_expense_entity.user_id
        )

        assert len(expenses) == 1
        assert isinstance(expenses[0], ExpenseDTO)
        assert expenses[0] == unique_expense_dto

    async def test_get_expenses_by_user_id_and_date_range_success(
        self, unique_expense_entity, unique_expense_dto
    ):
        await self._create_expense(unique_expense_entity)
        start_date = unique_expense_entity.date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_date = unique_expense_entity.date.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        expenses = await self.expense_use_cases.get_expenses_by_user_id_and_date_range(
            user_id=unique_expense_entity.user_id,
            start_date=start_date,
            end_date=end_date,
        )

        assert len(expenses) == 1
        assert isinstance(expenses[0], ExpenseDTO)
        assert expenses[0] == unique_expense_dto

    async def test_get_expenses_by_user_id_and_category_id_success(
        self, unique_expense_entity, unique_expense_dto
    ):
        await self._create_expense(unique_expense_entity)
        expenses = await self.expense_use_cases.get_expenses_by_user_id_and_category_id(
            user_id=unique_expense_entity.user_id,
            category_id=unique_expense_entity.category_id,
        )

        assert len(expenses) == 1
        assert isinstance(expenses[0], ExpenseDTO)
        assert expenses[0] == unique_expense_dto

    async def test_create_expense_success(
        self, unique_expense_create_dto, unique_expense_dto
    ):
        before_create = datetime.now(timezone.utc)
        expense = await self.expense_use_cases.create_expense(
            expense_data=unique_expense_create_dto
        )
        after_create = datetime.now(timezone.utc)

        assert isinstance(expense, ExpenseDTO)
        assert expense.amount == unique_expense_dto.amount
        assert expense.user_id == unique_expense_dto.user_id
        assert expense.category_id == unique_expense_dto.category_id
        assert before_create <= expense.created_at <= after_create
        assert before_create <= expense.updated_at <= after_create

    async def test_update_expense_success(
        self, unique_expense_entity_with_times, unique_expense_update_dto
    ):
        expense, before_create, after_create = unique_expense_entity_with_times
        await self._create_expense(expense)

        before_update = datetime.now(timezone.utc)
        updated_expense = await self.expense_use_cases.update_expense(
            unique_expense_update_dto
        )
        after_update = datetime.now(timezone.utc)

        assert isinstance(updated_expense, ExpenseDTO)
        assert updated_expense.amount == unique_expense_update_dto.amount
        assert updated_expense.description == unique_expense_update_dto.description
        assert before_create <= updated_expense.created_at <= after_create
        assert before_update <= updated_expense.updated_at <= after_update

    async def test_update_expense_partial_data(self, unique_expense_entity_with_times):
        expense, before_create, after_create = unique_expense_entity_with_times
        await self._create_expense(expense)

        partial_update_dto = ExpenseUpdateDTO(
            id=expense.id,
            amount=999.99,
            date=None,
            category_id=None,
            description=None,
        )

        before_update = datetime.now(timezone.utc)
        updated_expense = await self.expense_use_cases.update_expense(
            partial_update_dto
        )
        after_update = datetime.now(timezone.utc)

        assert updated_expense.amount == 999.99
        assert updated_expense.date == expense.date
        assert updated_expense.category_id == expense.category_id
        assert updated_expense.description == expense.description
        assert before_update <= updated_expense.updated_at <= after_update

    async def test_update_expense_not_found(
        self, unique_expense_update_dto, random_uuid
    ):
        unique_expense_update_dto.id = random_uuid
        with pytest.raises(ExpenseNotFound):
            await self.expense_use_cases.update_expense(unique_expense_update_dto)

    async def test_delete_expense_success(self, unique_expense_entity):
        new_expense = await self._create_expense(unique_expense_entity)
        result = await self.expense_use_cases.delete_expense(expense_id=new_expense.id)

        assert result is None

    async def test_delete_expense_not_found(self, random_uuid):
        with pytest.raises(ExpenseNotFound):
            await self.expense_use_cases.delete_expense(expense_id=random_uuid)
