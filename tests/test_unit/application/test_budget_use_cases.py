from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from pytest_asyncio import fixture

from expenses_tracker.application.dto.budget import (
    BudgetDTO,
    BudgetCreateDTO,
    BudgetUpdateDTO,
)
from expenses_tracker.application.use_cases.budget import BudgetUseCases
from expenses_tracker.core.constants import BudgetPeriod
from expenses_tracker.domain.entities.budget import Budget
from expenses_tracker.domain.exceptions.budget import BudgetNotFound
from expenses_tracker.domain.repositories.uow import IUnitOfWork


@fixture
def budget_entity():
    return Budget(
        id=uuid4(),
        amount=1000.0,
        period=BudgetPeriod.MONTHLY,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 31),
        user_id=uuid4(),
        category_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@fixture
def budget_dto(budget_entity):
    return BudgetDTO(
        id=budget_entity.id,
        amount=budget_entity.amount,
        period=budget_entity.period,
        start_date=budget_entity.start_date,
        end_date=budget_entity.end_date,
        user_id=budget_entity.user_id,
        category_id=budget_entity.category_id,
        created_at=budget_entity.created_at,
        updated_at=budget_entity.updated_at,
    )


@fixture
def budget_create_dto(budget_entity):
    return BudgetCreateDTO(
        amount=budget_entity.amount,
        period=budget_entity.period,
        start_date=budget_entity.start_date,
        end_date=budget_entity.end_date,
        user_id=budget_entity.user_id,
        category_id=budget_entity.category_id,
    )


@fixture
def budget_update_dto(budget_entity):
    return BudgetUpdateDTO(
        id=budget_entity.id,
        amount=1500.0,
        period=BudgetPeriod.WEEKLY,
        start_date=datetime(2024, 2, 1),
        end_date=datetime(2024, 2, 28),
        category_id=uuid4(),
    )


@fixture
def mock_unit_of_work():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    mock_uow.__aenter__ = AsyncMock()
    mock_uow.__aexit__ = AsyncMock(return_value=False)
    mock_budget_repo = AsyncMock()
    mock_uow.__aenter__.return_value.budget_repository = mock_budget_repo
    return mock_uow


@fixture()
def random_uuid():
    return uuid4()


class TestBudgetUseCases:
    @fixture(autouse=True)
    def setup(self, mock_unit_of_work):
        self.budget_use_cases = BudgetUseCases(unit_of_work=mock_unit_of_work)
        self.mock_unit_of_work = mock_unit_of_work

    async def test_get_budget_success(
        self, mock_unit_of_work, budget_entity, budget_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_by_id.return_value = budget_entity
        budget = await self.budget_use_cases.get_budget(budget_id=budget_entity.id)

        assert isinstance(budget, BudgetDTO)
        assert budget.id == budget_dto.id
        assert budget.amount == budget_dto.amount
        assert budget.period == budget_dto.period
        mock_repo.get_by_id.assert_called_once_with(budget_id=budget_entity.id)

    async def test_get_budget_not_found(self, mock_unit_of_work, random_uuid):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_by_id.return_value = None

        with pytest.raises(BudgetNotFound):
            await self.budget_use_cases.get_budget(budget_id=random_uuid)
        mock_repo.get_by_id.assert_called_once_with(budget_id=random_uuid)

    async def test_get_budgets_by_user_id_success(
        self, mock_unit_of_work, budget_entity, budget_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_all_by_user_id.return_value = [budget_entity]
        budgets = await self.budget_use_cases.get_budgets_by_user_id(
            user_id=budget_entity.user_id
        )

        assert len(budgets) == 1
        assert isinstance(budgets[0], BudgetDTO)
        assert budgets[0].id == budget_dto.id
        assert budgets[0].amount == budget_dto.amount
        mock_repo.get_all_by_user_id.assert_called_once_with(
            user_id=budget_entity.user_id
        )

    async def test_get_budgets_by_user_id_empty(self, mock_unit_of_work, random_uuid):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_all_by_user_id.return_value = []
        budgets = await self.budget_use_cases.get_budgets_by_user_id(
            user_id=random_uuid
        )

        assert len(budgets) == 0
        mock_repo.get_all_by_user_id.assert_called_once_with(user_id=random_uuid)

    async def test_get_budgets_by_user_id_and_date_range_success(
        self, mock_unit_of_work, budget_entity, budget_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_by_user_id_and_date_range.return_value = [budget_entity]
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

        budgets = await self.budget_use_cases.get_budgets_by_user_id_and_date_range(
            user_id=budget_entity.user_id, start_date=start_date, end_date=end_date
        )

        assert len(budgets) == 1
        assert isinstance(budgets[0], BudgetDTO)
        assert budgets[0].id == budget_dto.id
        mock_repo.get_by_user_id_and_date_range.assert_called_once_with(
            user_id=budget_entity.user_id, start_date=start_date, end_date=end_date
        )

    async def test_get_budgets_by_user_id_and_category_id_success(
        self, mock_unit_of_work, budget_entity, budget_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_by_user_id_and_category_id.return_value = [budget_entity]

        budgets = await self.budget_use_cases.get_budgets_by_user_id_and_category_id(
            user_id=budget_entity.user_id, category_id=budget_entity.category_id
        )

        assert len(budgets) == 1
        assert isinstance(budgets[0], BudgetDTO)
        assert budgets[0].id == budget_dto.id
        mock_repo.get_by_user_id_and_category_id.assert_called_once_with(
            user_id=budget_entity.user_id, category_id=budget_entity.category_id
        )

    async def test_get_active_budgets_by_user_id_success(
        self, mock_unit_of_work, budget_entity, budget_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_active_budgets_by_user_id.return_value = [budget_entity]
        current_date = datetime(2024, 1, 15, tzinfo=timezone.utc)

        budgets = await self.budget_use_cases.get_active_budgets_by_user_id(
            user_id=budget_entity.user_id, current_date=current_date
        )

        assert len(budgets) == 1
        assert isinstance(budgets[0], BudgetDTO)
        assert budgets[0].id == budget_dto.id
        mock_repo.get_active_budgets_by_user_id.assert_called_once_with(
            user_id=budget_entity.user_id, current_date=current_date
        )

    async def test_get_budgets_by_user_id_and_period_success(
        self, mock_unit_of_work, budget_entity, budget_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_by_user_id_and_period.return_value = [budget_entity]

        budgets = await self.budget_use_cases.get_budgets_by_user_id_and_period(
            user_id=budget_entity.user_id, period=BudgetPeriod.MONTHLY
        )

        assert len(budgets) == 1
        assert isinstance(budgets[0], BudgetDTO)
        assert budgets[0].id == budget_dto.id
        mock_repo.get_by_user_id_and_period.assert_called_once_with(
            user_id=budget_entity.user_id, period=BudgetPeriod.MONTHLY
        )

    async def test_create_budget_success(
        self, mock_unit_of_work, budget_entity, budget_create_dto, budget_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.create.return_value = budget_entity
        budget = await self.budget_use_cases.create_budget(
            budget_data=budget_create_dto
        )

        assert isinstance(budget, BudgetDTO)
        assert budget.id == budget_dto.id
        assert budget.amount == budget_dto.amount
        assert budget.period == budget_dto.period
        mock_repo.create.assert_called_once()
        created_budget = mock_repo.create.call_args[1]["budget"]
        assert created_budget.user_id == budget_create_dto.user_id
        assert created_budget.amount == budget_create_dto.amount

    async def test_update_budget_success(
        self, mock_unit_of_work, budget_entity, budget_update_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_by_id.return_value = budget_entity
        mock_repo.update.return_value = budget_entity
        budget = await self.budget_use_cases.update_budget(
            budget_data=budget_update_dto
        )

        assert isinstance(budget, BudgetDTO)
        assert budget.id == budget_entity.id
        assert budget.amount == budget_update_dto.amount
        assert budget.period == budget_update_dto.period
        assert budget.start_date == budget_update_dto.start_date
        assert budget.end_date == budget_update_dto.end_date
        assert budget.category_id == budget_update_dto.category_id
        mock_repo.get_by_id.assert_called_once_with(budget_id=budget_entity.id)
        mock_repo.update.assert_called_once_with(budget=budget_entity)

    async def test_update_budget_partial_data(self, mock_unit_of_work, budget_entity):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_by_id.return_value = budget_entity
        mock_repo.update.return_value = budget_entity
        partial_update_dto = BudgetUpdateDTO(
            id=budget_entity.id,
            amount=2000.0,
            period=None,
            start_date=None,
            end_date=None,
            category_id=None,
        )

        budget = await self.budget_use_cases.update_budget(
            budget_data=partial_update_dto
        )

        assert budget.amount == 2000.0
        assert budget.period == budget_entity.period
        assert budget.start_date == budget_entity.start_date
        assert budget.end_date == budget_entity.end_date
        assert budget.category_id == budget_entity.category_id

    async def test_update_budget_not_found(
        self, mock_unit_of_work, budget_update_dto, random_uuid
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_by_id.return_value = None
        budget_update_dto.id = random_uuid

        with pytest.raises(BudgetNotFound):
            await self.budget_use_cases.update_budget(budget_data=budget_update_dto)
        mock_repo.get_by_id.assert_called_once_with(budget_id=random_uuid)

    async def test_delete_budget_success(self, mock_unit_of_work, budget_entity):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_by_id.return_value = budget_entity
        mock_repo.delete.return_value = None
        await self.budget_use_cases.delete_budget(budget_id=budget_entity.id)

        mock_repo.get_by_id.assert_called_once_with(budget_id=budget_entity.id)
        mock_repo.delete.assert_called_once_with(budget=budget_entity)

    async def test_delete_budget_not_found(self, mock_unit_of_work, random_uuid):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_by_id.return_value = None

        with pytest.raises(BudgetNotFound):
            await self.budget_use_cases.delete_budget(budget_id=random_uuid)
        mock_repo.get_by_id.assert_called_once_with(budget_id=random_uuid)

    async def test_get_total_budget_amount_for_period_success(
        self, mock_unit_of_work, budget_entity
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.budget_repository
        mock_repo.get_total_budget_amount_for_period.return_value = 1000.0
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

        total_amount = await self.budget_use_cases.get_total_budget_amount_for_period(
            user_id=budget_entity.user_id, start_date=start_date, end_date=end_date
        )

        assert total_amount == 1000.0
        mock_repo.get_total_budget_amount_for_period.assert_called_once_with(
            user_id=budget_entity.user_id, start_date=start_date, end_date=end_date
        )
