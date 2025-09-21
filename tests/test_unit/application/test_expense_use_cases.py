from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pytest_asyncio import fixture

from expenses_tracker.application.dto.expense import (
    ExpenseDTO,
    ExpenseCreateDTO,
    ExpenseUpdateDTO,
)
from expenses_tracker.application.use_cases.expense import ExpenseUseCases
from expenses_tracker.domain.entities.expense import Expense
from expenses_tracker.domain.exceptions.expense import ExpenseNotFound


@fixture
def expense_entity():
    return Expense(
        id=uuid4(),
        amount=100.50,
        date=datetime.now(timezone.utc),
        user_id=uuid4(),
        category_id=uuid4(),
        description="Groceries",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@fixture
def expense_dto(expense_entity):
    return ExpenseDTO(
        id=expense_entity.id,
        amount=expense_entity.amount,
        date=expense_entity.date,
        user_id=expense_entity.user_id,
        category_id=expense_entity.category_id,
        description=expense_entity.description,
        created_at=expense_entity.created_at,
        updated_at=expense_entity.updated_at,
    )


@fixture
def expense_create_dto(expense_entity):
    return ExpenseCreateDTO(
        amount=expense_entity.amount,
        date=expense_entity.date,
        user_id=expense_entity.user_id,
        category_id=expense_entity.category_id,
        description=expense_entity.description,
    )


@fixture
def expense_update_dto(expense_entity):
    return ExpenseUpdateDTO(
        id=expense_entity.id,
        amount=200.75,
        date=datetime.now(timezone.utc),
        category_id=uuid4(),
        description="Updated groceries",
    )


class TestExpenseUseCases:
    @fixture(autouse=True)
    def setup(self, mock_unit_of_work):
        self.expense_use_cases = ExpenseUseCases(unit_of_work=mock_unit_of_work)
        self.mock_unit_of_work = mock_unit_of_work

    async def test_get_expense_success(
        self, mock_unit_of_work, expense_entity, expense_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.expense_repository
        mock_repo.get_by_id.return_value = expense_entity
        expense = await self.expense_use_cases.get_expense(expense_id=expense_entity.id)

        assert isinstance(expense, ExpenseDTO)
        assert expense.id == expense_dto.id
        assert expense.amount == expense_dto.amount
        assert expense.description == expense_dto.description
        mock_repo.get_by_id.assert_called_once_with(expense_id=expense_entity.id)

    async def test_get_expense_not_found(self, mock_unit_of_work, random_uuid):
        mock_repo = mock_unit_of_work.__aenter__.return_value.expense_repository
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ExpenseNotFound):
            await self.expense_use_cases.get_expense(expense_id=random_uuid)
        mock_repo.get_by_id.assert_called_once_with(expense_id=random_uuid)

    async def test_get_expenses_by_user_id_success(
        self, mock_unit_of_work, expense_entity, expense_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.expense_repository
        mock_repo.get_all_by_user_id.return_value = [expense_entity]
        expenses = await self.expense_use_cases.get_expenses_by_user_id(
            user_id=expense_entity.user_id
        )

        assert len(expenses) == 1
        assert isinstance(expenses[0], ExpenseDTO)
        assert expenses[0].id == expense_dto.id
        assert expenses[0].amount == expense_dto.amount
        mock_repo.get_all_by_user_id.assert_called_once_with(
            user_id=expense_entity.user_id
        )

    async def test_get_expenses_by_user_id_empty(self, mock_unit_of_work, random_uuid):
        mock_repo = mock_unit_of_work.__aenter__.return_value.expense_repository
        mock_repo.get_all_by_user_id.return_value = []
        expenses = await self.expense_use_cases.get_expenses_by_user_id(
            user_id=random_uuid
        )

        assert len(expenses) == 0
        mock_repo.get_all_by_user_id.assert_called_once_with(user_id=random_uuid)

    async def test_get_expenses_by_user_id_and_date_range_success(
        self, mock_unit_of_work, expense_entity, expense_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.expense_repository
        mock_repo.get_by_user_id_and_date_range.return_value = [expense_entity]
        start_date = datetime.now(timezone.utc)
        end_date = datetime.now(timezone.utc)

        expenses = await self.expense_use_cases.get_expenses_by_user_id_and_date_range(
            user_id=expense_entity.user_id, start_date=start_date, end_date=end_date
        )

        assert len(expenses) == 1
        assert isinstance(expenses[0], ExpenseDTO)
        assert expenses[0].id == expense_dto.id
        mock_repo.get_by_user_id_and_date_range.assert_called_once_with(
            user_id=expense_entity.user_id, start_date=start_date, end_date=end_date
        )

    async def test_get_expenses_by_user_id_and_category_id_success(
        self, mock_unit_of_work, expense_entity, expense_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.expense_repository
        mock_repo.get_by_user_id_and_category_id.return_value = [expense_entity]

        expenses = await self.expense_use_cases.get_expenses_by_user_id_and_category_id(
            user_id=expense_entity.user_id, category_id=expense_entity.category_id
        )

        assert len(expenses) == 1
        assert isinstance(expenses[0], ExpenseDTO)
        assert expenses[0].id == expense_dto.id
        mock_repo.get_by_user_id_and_category_id.assert_called_once_with(
            user_id=expense_entity.user_id, category_id=expense_entity.category_id
        )

    async def test_create_expense_success(
        self, mock_unit_of_work, expense_entity, expense_create_dto, expense_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.expense_repository
        mock_repo.create.return_value = expense_entity
        expense = await self.expense_use_cases.create_expense(
            expense_data=expense_create_dto
        )

        assert isinstance(expense, ExpenseDTO)
        assert expense.id == expense_dto.id
        assert expense.amount == expense_dto.amount
        assert expense.description == expense_dto.description
        mock_repo.create.assert_called_once()
        created_expense = mock_repo.create.call_args[1]["expense"]
        assert created_expense.user_id == expense_create_dto.user_id
        assert created_expense.amount == expense_create_dto.amount

    async def test_update_expense_success(
        self, mock_unit_of_work, expense_entity, expense_update_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.expense_repository
        mock_repo.get_by_id.return_value = expense_entity
        mock_repo.update.return_value = expense_entity
        expense = await self.expense_use_cases.update_expense(
            expense_data=expense_update_dto
        )

        assert isinstance(expense, ExpenseDTO)
        assert expense.id == expense_entity.id
        assert expense.amount == expense_update_dto.amount
        assert expense.description == expense_update_dto.description
        mock_repo.get_by_id.assert_called_once_with(expense_id=expense_entity.id)
        mock_repo.update.assert_called_once_with(expense=expense_entity)

    async def test_update_expense_partial_data(self, mock_unit_of_work, expense_entity):
        mock_repo = mock_unit_of_work.__aenter__.return_value.expense_repository
        mock_repo.get_by_id.return_value = expense_entity
        mock_repo.update.return_value = expense_entity
        partial_update_dto = ExpenseUpdateDTO(
            id=expense_entity.id,
            amount=150.25,
            date=None,
            category_id=None,
            description=None,
        )

        expense = await self.expense_use_cases.update_expense(
            expense_data=partial_update_dto
        )

        assert expense.amount == 150.25
        assert expense.date == expense_entity.date
        assert expense.category_id == expense_entity.category_id
        assert expense.description == expense_entity.description

    async def test_update_expense_not_found(
        self, mock_unit_of_work, expense_update_dto, random_uuid
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.expense_repository
        mock_repo.get_by_id.return_value = None
        expense_update_dto.id = random_uuid

        with pytest.raises(ExpenseNotFound):
            await self.expense_use_cases.update_expense(expense_data=expense_update_dto)
        mock_repo.get_by_id.assert_called_once_with(expense_id=random_uuid)

    async def test_delete_expense_success(self, mock_unit_of_work, expense_entity):
        mock_repo = mock_unit_of_work.__aenter__.return_value.expense_repository
        mock_repo.get_by_id.return_value = expense_entity
        mock_repo.delete.return_value = None
        await self.expense_use_cases.delete_expense(expense_id=expense_entity.id)

        mock_repo.get_by_id.assert_called_once_with(expense_id=expense_entity.id)
        mock_repo.delete.assert_called_once_with(expense=expense_entity)

    async def test_delete_expense_not_found(self, mock_unit_of_work, random_uuid):
        mock_repo = mock_unit_of_work.__aenter__.return_value.expense_repository
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ExpenseNotFound):
            await self.expense_use_cases.delete_expense(expense_id=random_uuid)
        mock_repo.get_by_id.assert_called_once_with(expense_id=random_uuid)
