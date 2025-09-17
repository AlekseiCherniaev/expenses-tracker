from datetime import datetime, timezone
from uuid import UUID

import structlog

from expenses_tracker.application.dto.budget import (
    BudgetDTO,
    BudgetCreateDTO,
    BudgetUpdateDTO,
)
from expenses_tracker.core.constants import BudgetPeriod
from expenses_tracker.domain.entities.budget import Budget
from expenses_tracker.domain.exceptions.budget import BudgetNotFound
from expenses_tracker.domain.repositories.uow import IUnitOfWork

logger = structlog.get_logger(__name__)


class BudgetUseCases:
    def __init__(self, unit_of_work: IUnitOfWork):
        self._unit_of_work = unit_of_work

    async def get_budget(self, budget_id: UUID) -> BudgetDTO | None:
        async with self._unit_of_work as uow:
            budget = await uow.budget_repository.get_by_id(budget_id=budget_id)
            if not budget:
                raise BudgetNotFound(f"Budget with id {budget_id} not found")
            logger.bind(budget=budget).debug("Retrieved budget from repo")
            return BudgetDTO(
                id=budget.id,
                amount=budget.amount,
                period=budget.period,
                start_date=budget.start_date,
                end_date=budget.end_date,
                user_id=budget.user_id,
                category_id=budget.category_id,
                created_at=budget.created_at,
                updated_at=budget.updated_at,
            )
        assert False, "unreachable"

    async def get_budgets_by_user_id(self, user_id: UUID) -> list[BudgetDTO]:
        async with self._unit_of_work as uow:
            budgets = await uow.budget_repository.get_all_by_user_id(user_id=user_id)
            logger.bind(budgets=budgets).debug("Retrieved budgets from repo")
            return [
                BudgetDTO(
                    id=budget.id,
                    amount=budget.amount,
                    period=budget.period,
                    start_date=budget.start_date,
                    end_date=budget.end_date,
                    user_id=budget.user_id,
                    category_id=budget.category_id,
                    created_at=budget.created_at,
                    updated_at=budget.updated_at,
                )
                for budget in budgets
            ]
        assert False, "unreachable"

    async def get_budgets_by_user_id_and_date_range(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[BudgetDTO]:
        async with self._unit_of_work as uow:
            budgets = await uow.budget_repository.get_by_user_id_and_date_range(
                user_id=user_id, start_date=start_date, end_date=end_date
            )
            logger.bind(budgets=budgets).debug(
                "Retrieved budgets by date range from repo"
            )
            return [
                BudgetDTO(
                    id=budget.id,
                    amount=budget.amount,
                    period=budget.period,
                    start_date=budget.start_date,
                    end_date=budget.end_date,
                    user_id=budget.user_id,
                    category_id=budget.category_id,
                    created_at=budget.created_at,
                    updated_at=budget.updated_at,
                )
                for budget in budgets
            ]
        assert False, "unreachable"

    async def get_budgets_by_user_id_and_category_id(
        self, user_id: UUID, category_id: UUID
    ) -> list[BudgetDTO]:
        async with self._unit_of_work as uow:
            budgets = await uow.budget_repository.get_by_user_id_and_category_id(
                user_id=user_id, category_id=category_id
            )
            logger.bind(budgets=budgets).debug(
                "Retrieved budgets by category from repo"
            )
            return [
                BudgetDTO(
                    id=budget.id,
                    amount=budget.amount,
                    period=budget.period,
                    start_date=budget.start_date,
                    end_date=budget.end_date,
                    user_id=budget.user_id,
                    category_id=budget.category_id,
                    created_at=budget.created_at,
                    updated_at=budget.updated_at,
                )
                for budget in budgets
            ]
        assert False, "unreachable"

    async def get_active_budgets_by_user_id(
        self, user_id: UUID, current_date: datetime
    ) -> list[BudgetDTO]:
        async with self._unit_of_work as uow:
            budgets = await uow.budget_repository.get_active_budgets_by_user_id(
                user_id=user_id, current_date=current_date
            )
            logger.bind(budgets=budgets).debug("Retrieved active budgets from repo")
            return [
                BudgetDTO(
                    id=budget.id,
                    amount=budget.amount,
                    period=budget.period,
                    start_date=budget.start_date,
                    end_date=budget.end_date,
                    user_id=budget.user_id,
                    category_id=budget.category_id,
                    created_at=budget.created_at,
                    updated_at=budget.updated_at,
                )
                for budget in budgets
            ]
        assert False, "unreachable"

    async def get_budgets_by_user_id_and_period(
        self, user_id: UUID, period: BudgetPeriod
    ) -> list[BudgetDTO]:
        async with self._unit_of_work as uow:
            budgets = await uow.budget_repository.get_by_user_id_and_period(
                user_id=user_id, period=period
            )
            logger.bind(budgets=budgets).debug("Retrieved budgets by period from repo")
            return [
                BudgetDTO(
                    id=budget.id,
                    amount=budget.amount,
                    period=budget.period,
                    start_date=budget.start_date,
                    end_date=budget.end_date,
                    user_id=budget.user_id,
                    category_id=budget.category_id,
                    created_at=budget.created_at,
                    updated_at=budget.updated_at,
                )
                for budget in budgets
            ]
        assert False, "unreachable"

    async def create_budget(self, budget_data: BudgetCreateDTO) -> BudgetDTO:
        async with self._unit_of_work as uow:
            new_budget = Budget(
                amount=budget_data.amount,
                period=budget_data.period,
                start_date=budget_data.start_date,
                end_date=budget_data.end_date,
                user_id=budget_data.user_id,
                category_id=budget_data.category_id,
            )
            budget = await uow.budget_repository.create(budget=new_budget)
            logger.bind(budget=budget).debug("Created budget from repo")
            return BudgetDTO(
                id=budget.id,
                amount=budget.amount,
                period=budget.period,
                start_date=budget.start_date,
                end_date=budget.end_date,
                user_id=budget.user_id,
                category_id=budget.category_id,
                created_at=budget.created_at,
                updated_at=budget.updated_at,
            )
        assert False, "unreachable"

    async def update_budget(self, budget_data: BudgetUpdateDTO) -> BudgetDTO | None:
        async with self._unit_of_work as uow:
            budget = await uow.budget_repository.get_by_id(budget_id=budget_data.id)
            if not budget:
                raise BudgetNotFound(f"Budget with id {budget_data.id} not found")

            if budget_data.amount is not None:
                budget.amount = budget_data.amount
            if budget_data.period is not None:
                budget.period = budget_data.period
            if budget_data.start_date is not None:
                budget.start_date = budget_data.start_date
            if budget_data.end_date is not None:
                budget.end_date = budget_data.end_date
            if budget_data.category_id is not None:
                budget.category_id = budget_data.category_id

            budget.updated_at = datetime.now(timezone.utc)
            updated_budget = await uow.budget_repository.update(budget=budget)
            logger.bind(updated_budget=updated_budget).debug("Updated budget from repo")

            return BudgetDTO(
                id=updated_budget.id,
                amount=updated_budget.amount,
                period=updated_budget.period,
                start_date=updated_budget.start_date,
                end_date=updated_budget.end_date,
                user_id=updated_budget.user_id,
                category_id=updated_budget.category_id,
                created_at=updated_budget.created_at,
                updated_at=updated_budget.updated_at,
            )
        assert False, "unreachable"

    async def delete_budget(self, budget_id: UUID) -> None:
        async with self._unit_of_work as uow:
            budget = await uow.budget_repository.get_by_id(budget_id=budget_id)
            if not budget:
                raise BudgetNotFound(f"Budget with id {budget_id} not found")
            await uow.budget_repository.delete(budget=budget)
            logger.bind(budget=budget).debug("Deleted budget from repo")
            return None
        assert False, "unreachable"

    async def get_total_budget_amount_for_period(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> float:
        async with self._unit_of_work as uow:
            total_amount = (
                await uow.budget_repository.get_total_budget_amount_for_period(
                    user_id=user_id, start_date=start_date, end_date=end_date
                )
            )
            logger.bind(total_amount=total_amount).debug(
                "Retrieved total budget amount from repo"
            )
            return total_amount
        assert False, "unreachable"
