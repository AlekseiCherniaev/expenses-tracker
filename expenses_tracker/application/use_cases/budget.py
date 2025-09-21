from datetime import datetime, timezone
from uuid import UUID

import structlog

from expenses_tracker.application.dto.budget import (
    BudgetDTO,
    BudgetCreateDTO,
    BudgetUpdateDTO,
)
from expenses_tracker.application.interfaces.cache_service import ICacheService
from expenses_tracker.core.constants import BudgetPeriod
from expenses_tracker.core.settings import get_settings
from expenses_tracker.domain.entities.budget import Budget
from expenses_tracker.domain.exceptions.budget import BudgetNotFound
from expenses_tracker.domain.repositories.uow import IUnitOfWork

logger = structlog.get_logger(__name__)


class BudgetUseCases:
    def __init__(
        self,
        unit_of_work: IUnitOfWork,
        cache_service: ICacheService[BudgetDTO | list[BudgetDTO]],
    ):
        self._unit_of_work = unit_of_work
        self._cache_service = cache_service

    @staticmethod
    def _to_dto(budget: Budget) -> BudgetDTO:
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

    @staticmethod
    def _budget_cache_key(budget_id: UUID) -> str:
        return f"budget:{budget_id}"

    @staticmethod
    def _user_budgets_cache_key(user_id: UUID) -> str:
        return f"budgets:user:{user_id}"

    async def get_budget(self, budget_id: UUID) -> BudgetDTO | None:
        cache_key = self._budget_cache_key(budget_id)
        cached_budget = await self._cache_service.get(
            key=cache_key, serializer=BudgetDTO
        )
        if cached_budget:
            logger.bind(budget_id=budget_id).debug("Retrieved budget from cache")
            return cached_budget  # type: ignore

        async with self._unit_of_work as uow:
            budget = await uow.budget_repository.get_by_id(budget_id=budget_id)
            if not budget:
                raise BudgetNotFound(f"Budget with id {budget_id} not found")

            dto = self._to_dto(budget)
            await self._cache_service.set(
                key=cache_key, value=dto, ttl=get_settings().budget_dto_ttl_seconds
            )
            logger.bind(budget_id=budget_id).debug(
                "Retrieved budget from repo and cached"
            )
            return dto
        assert False, "unreachable"

    async def get_budgets_by_user_id(self, user_id: UUID) -> list[BudgetDTO]:
        cache_key = self._user_budgets_cache_key(user_id)
        cached_budgets = await self._cache_service.get(
            key=cache_key, serializer=list[BudgetDTO]
        )
        if cached_budgets:
            logger.bind(user_id=user_id, count=len(cached_budgets)).debug(  # type: ignore
                "Retrieved budgets from cache"
            )
            return cached_budgets  # type: ignore

        async with self._unit_of_work as uow:
            budgets = await uow.budget_repository.get_all_by_user_id(user_id=user_id)
            dtos = [self._to_dto(b) for b in budgets]
            await self._cache_service.set(
                key=cache_key, value=dtos, ttl=get_settings().budgets_list_ttl_seconds
            )
            logger.bind(user_id=user_id, count=len(dtos)).debug(
                "Retrieved budgets from repo and cached"
            )
            return dtos
        assert False, "unreachable"

    async def get_budgets_by_user_id_and_date_range(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[BudgetDTO]:
        async with self._unit_of_work as uow:
            budgets = await uow.budget_repository.get_by_user_id_and_date_range(
                user_id=user_id, start_date=start_date, end_date=end_date
            )
            logger.bind(user_id=user_id, count=len(budgets)).debug(
                "Retrieved budgets by date range from repo"
            )
            return [self._to_dto(b) for b in budgets]
        assert False, "unreachable"

    async def get_budgets_by_user_id_and_category_id(
        self, user_id: UUID, category_id: UUID
    ) -> list[BudgetDTO]:
        async with self._unit_of_work as uow:
            budgets = await uow.budget_repository.get_by_user_id_and_category_id(
                user_id=user_id, category_id=category_id
            )
            logger.bind(user_id=user_id, count=len(budgets)).debug(
                "Retrieved budgets by category from repo"
            )
            return [self._to_dto(b) for b in budgets]
        assert False, "unreachable"

    async def get_active_budgets_by_user_id(
        self, user_id: UUID, current_date: datetime
    ) -> list[BudgetDTO]:
        async with self._unit_of_work as uow:
            budgets = await uow.budget_repository.get_active_budgets_by_user_id(
                user_id=user_id, current_date=current_date
            )
            logger.bind(user_id=user_id, count=len(budgets)).debug(
                "Retrieved active budgets from repo"
            )
            return [self._to_dto(b) for b in budgets]
        assert False, "unreachable"

    async def get_budgets_by_user_id_and_period(
        self, user_id: UUID, period: BudgetPeriod
    ) -> list[BudgetDTO]:
        async with self._unit_of_work as uow:
            budgets = await uow.budget_repository.get_by_user_id_and_period(
                user_id=user_id, period=period
            )
            logger.bind(user_id=user_id, count=len(budgets)).debug(
                "Retrieved budgets by period from repo"
            )
            return [self._to_dto(b) for b in budgets]
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
            logger.bind(budget=budget).debug("Created budget in repo")

            dto = self._to_dto(budget)
            await self._cache_service.set(
                key=self._budget_cache_key(dto.id),
                value=dto,
                ttl=get_settings().budget_dto_ttl_seconds,
            )
            # invalidate user budgets cache
            await self._cache_service.delete(
                key=self._user_budgets_cache_key(budget.user_id)
            )
            return dto
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
            logger.bind(updated_budget=updated_budget).debug("Updated budget in repo")

            dto = self._to_dto(updated_budget)
            await self._cache_service.set(
                key=self._budget_cache_key(dto.id),
                value=dto,
                ttl=get_settings().budget_dto_ttl_seconds,
            )
            # invalidate user budgets cache
            await self._cache_service.delete(
                key=self._user_budgets_cache_key(dto.user_id)
            )
            return dto
        assert False, "unreachable"

    async def delete_budget(self, budget_id: UUID) -> None:
        async with self._unit_of_work as uow:
            budget = await uow.budget_repository.get_by_id(budget_id=budget_id)
            if not budget:
                raise BudgetNotFound(f"Budget with id {budget_id} not found")

            await uow.budget_repository.delete(budget=budget)
            logger.bind(budget=budget).debug("Deleted budget in repo")

            await self._cache_service.delete(key=self._budget_cache_key(budget_id))
            await self._cache_service.delete(
                key=self._user_budgets_cache_key(budget.user_id)
            )
            return None
