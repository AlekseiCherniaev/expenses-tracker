from datetime import datetime, timezone, timedelta

import pytest
from pytest import fixture

from expenses_tracker.application.dto.budget import (
    BudgetDTO,
)
from expenses_tracker.application.use_cases.budget import BudgetUseCases
from expenses_tracker.domain.entities.budget import Budget
from expenses_tracker.domain.exceptions.budget import BudgetNotFound


class TestBudgetUseCases:
    @fixture(autouse=True)
    def setup(self, unit_of_work):
        self.budget_use_cases = BudgetUseCases(unit_of_work=unit_of_work)
        self.unit_of_work = unit_of_work

    async def _create_budget(self, budget_entity: Budget) -> Budget:
        async with self.unit_of_work as uow:
            return await uow.budget_repository.create(budget_entity)

    async def test_get_budget_success(self, unique_budget_entity, unique_budget_dto):
        new_budget = await self._create_budget(unique_budget_entity)
        budget = await self.budget_use_cases.get_budget(budget_id=new_budget.id)

        assert isinstance(budget, BudgetDTO)
        assert budget.amount == unique_budget_dto.amount
        assert budget.period == unique_budget_dto.period
        assert budget.user_id == unique_budget_dto.user_id
        assert budget.category_id == unique_budget_dto.category_id

    async def test_get_budget_not_found(self, random_uuid):
        with pytest.raises(BudgetNotFound):
            await self.budget_use_cases.get_budget(budget_id=random_uuid)

    async def test_get_budgets_by_user_id_success(
        self, unique_budget_entity, unique_budget_dto
    ):
        await self._create_budget(unique_budget_entity)
        budgets = await self.budget_use_cases.get_budgets_by_user_id(
            user_id=unique_budget_entity.user_id
        )

        assert len(budgets) == 1
        assert isinstance(budgets[0], BudgetDTO)
        assert budgets[0].amount == unique_budget_dto.amount
        assert budgets[0].user_id == unique_budget_dto.user_id

    async def test_get_budgets_by_user_id_and_date_range_success(
        self, unique_budget_entity
    ):
        await self._create_budget(unique_budget_entity)

        start_date = unique_budget_entity.start_date - timedelta(days=1)
        end_date = unique_budget_entity.end_date + timedelta(days=1)

        budgets = await self.budget_use_cases.get_budgets_by_user_id_and_date_range(
            user_id=unique_budget_entity.user_id,
            start_date=start_date,
            end_date=end_date,
        )

        assert len(budgets) == 1
        assert budgets[0].id == unique_budget_entity.id

    async def test_get_budgets_by_user_id_and_category_id_success(
        self, unique_budget_entity
    ):
        await self._create_budget(unique_budget_entity)

        budgets = await self.budget_use_cases.get_budgets_by_user_id_and_category_id(
            user_id=unique_budget_entity.user_id,
            category_id=unique_budget_entity.category_id,
        )

        assert len(budgets) == 1
        assert budgets[0].id == unique_budget_entity.id
        assert budgets[0].category_id == unique_budget_entity.category_id

    async def test_get_active_budgets_by_user_id_success(self, unique_budget_entity):
        await self._create_budget(unique_budget_entity)

        current_date = datetime.now()
        budgets = await self.budget_use_cases.get_active_budgets_by_user_id(
            user_id=unique_budget_entity.user_id, current_date=current_date
        )

        assert len(budgets) == 1
        assert budgets[0].id == unique_budget_entity.id

    async def test_get_budgets_by_user_id_and_period_success(
        self, unique_budget_entity
    ):
        await self._create_budget(unique_budget_entity)

        budgets = await self.budget_use_cases.get_budgets_by_user_id_and_period(
            user_id=unique_budget_entity.user_id, period=unique_budget_entity.period
        )

        assert len(budgets) == 1
        assert budgets[0].id == unique_budget_entity.id
        assert budgets[0].period == unique_budget_entity.period

    async def test_create_budget_success(self, unique_budget_create_dto):
        before_create = datetime.now(timezone.utc)
        budget = await self.budget_use_cases.create_budget(
            budget_data=unique_budget_create_dto
        )
        after_create = datetime.now(timezone.utc)

        assert isinstance(budget, BudgetDTO)
        assert budget.amount == unique_budget_create_dto.amount
        assert budget.period == unique_budget_create_dto.period
        assert budget.user_id == unique_budget_create_dto.user_id
        assert budget.category_id == unique_budget_create_dto.category_id
        assert before_create <= budget.created_at <= after_create
        assert before_create <= budget.updated_at <= after_create

    async def test_update_budget_success(
        self, unique_budget_entity_with_times, unique_budget_update_dto
    ):
        budget, before_create, after_create = unique_budget_entity_with_times
        await self._create_budget(budget)

        before_update = datetime.now(timezone.utc)
        updated_budget = await self.budget_use_cases.update_budget(
            unique_budget_update_dto
        )
        after_update = datetime.now(timezone.utc)

        assert isinstance(updated_budget, BudgetDTO)
        assert updated_budget.amount == unique_budget_update_dto.amount
        assert updated_budget.period == unique_budget_update_dto.period
        assert updated_budget.start_date == unique_budget_update_dto.start_date
        assert updated_budget.end_date == unique_budget_update_dto.end_date
        assert before_create <= updated_budget.created_at <= after_create
        assert before_update <= updated_budget.updated_at <= after_update

    async def test_update_budget_not_found(self, unique_budget_update_dto, random_uuid):
        unique_budget_update_dto.id = random_uuid
        with pytest.raises(BudgetNotFound):
            await self.budget_use_cases.update_budget(unique_budget_update_dto)

    async def test_delete_budget_success(self, unique_budget_entity):
        new_budget = await self._create_budget(unique_budget_entity)
        result = await self.budget_use_cases.delete_budget(budget_id=new_budget.id)

        assert result is None

    async def test_delete_budget_not_found(self, random_uuid):
        with pytest.raises(BudgetNotFound):
            await self.budget_use_cases.delete_budget(budget_id=random_uuid)

    async def test_get_total_budget_amount_for_period_success(
        self, unique_budget_entity
    ):
        await self._create_budget(unique_budget_entity)

        start_date = unique_budget_entity.start_date - timedelta(days=1)
        end_date = unique_budget_entity.end_date + timedelta(days=1)

        total_amount = await self.budget_use_cases.get_total_budget_amount_for_period(
            user_id=unique_budget_entity.user_id,
            start_date=start_date,
            end_date=end_date,
        )

        assert total_amount == unique_budget_entity.amount
