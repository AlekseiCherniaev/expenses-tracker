from datetime import datetime
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends

from expenses_tracker.application.dto.budget import (
    BudgetCreateDTO,
    BudgetUpdateDTO,
)
from expenses_tracker.application.use_cases.budget import BudgetUseCases
from expenses_tracker.core.constants import BudgetPeriod
from expenses_tracker.infrastructure.api.schemas.budget import (
    InternalBudgetCreateRequest,
    InternalBudgetResponse,
    InternalBudgetUpdateRequest,
)
from expenses_tracker.infrastructure.di import get_budget_use_cases

router = APIRouter(prefix="/budgets", tags=["internal budgets"])

logger = structlog.get_logger(__name__)


@router.get("/get/{budget_id}")
async def get_internal_budget(
    budget_id: UUID,
    budget_use_cases: BudgetUseCases = Depends(get_budget_use_cases),
) -> InternalBudgetResponse:
    logger.bind(budget_id=budget_id).debug("Getting budget...")
    budget_dto = await budget_use_cases.get_budget(budget_id=budget_id)
    logger.bind(budget=budget_dto).debug("Got budget")
    return InternalBudgetResponse(**budget_dto.__dict__)


@router.get("/get-by-user/{user_id}")
async def get_internal_budgets_by_user(
    user_id: UUID,
    budget_use_cases: BudgetUseCases = Depends(get_budget_use_cases),
) -> list[InternalBudgetResponse]:
    logger.bind(user_id=user_id).debug("Getting budgets for user...")
    budget_dtos = await budget_use_cases.get_budgets_by_user_id(user_id=user_id)
    logger.bind(budgets=budget_dtos).debug("Got budgets")
    return [InternalBudgetResponse(**dto.__dict__) for dto in budget_dtos]


@router.get("/get-by-user-date-range/{user_id}")
async def get_internal_budgets_by_user_and_date_range(
    user_id: UUID,
    start_date: datetime,
    end_date: datetime,
    budget_use_cases: BudgetUseCases = Depends(get_budget_use_cases),
) -> list[InternalBudgetResponse]:
    logger.bind(user_id=user_id, start_date=start_date, end_date=end_date).debug(
        "Getting budgets for user by date range..."
    )
    budget_dtos = await budget_use_cases.get_budgets_by_user_id_and_date_range(
        user_id=user_id, start_date=start_date, end_date=end_date
    )
    logger.bind(budgets=budget_dtos).debug("Got budgets by date range")
    return [InternalBudgetResponse(**dto.__dict__) for dto in budget_dtos]


@router.get("/get-by-user-category/{user_id}/{category_id}")
async def get_internal_budgets_by_user_and_category(
    user_id: UUID,
    category_id: UUID,
    budget_use_cases: BudgetUseCases = Depends(get_budget_use_cases),
) -> list[InternalBudgetResponse]:
    logger.bind(user_id=user_id, category_id=category_id).debug(
        "Getting budgets for user by category..."
    )
    budget_dtos = await budget_use_cases.get_budgets_by_user_id_and_category_id(
        user_id=user_id, category_id=category_id
    )
    logger.bind(budgets=budget_dtos).debug("Got budgets by category")
    return [InternalBudgetResponse(**dto.__dict__) for dto in budget_dtos]


@router.get("/get-active-by-user/{user_id}")
async def get_internal_active_budgets_by_user(
    user_id: UUID,
    current_date: datetime,
    budget_use_cases: BudgetUseCases = Depends(get_budget_use_cases),
) -> list[InternalBudgetResponse]:
    logger.bind(user_id=user_id, current_date=current_date).debug(
        "Getting active budgets for user..."
    )
    budget_dtos = await budget_use_cases.get_active_budgets_by_user_id(
        user_id=user_id, current_date=current_date
    )
    logger.bind(budgets=budget_dtos).debug("Got active budgets")
    return [InternalBudgetResponse(**dto.__dict__) for dto in budget_dtos]


@router.get("/get-by-user-period/{user_id}")
async def get_internal_budgets_by_user_and_period(
    user_id: UUID,
    period: BudgetPeriod,
    budget_use_cases: BudgetUseCases = Depends(get_budget_use_cases),
) -> list[InternalBudgetResponse]:
    logger.bind(user_id=user_id, period=period).debug(
        "Getting budgets for user by period..."
    )
    budget_dtos = await budget_use_cases.get_budgets_by_user_id_and_period(
        user_id=user_id, period=period
    )
    logger.bind(budgets=budget_dtos).debug("Got budgets by period")
    return [InternalBudgetResponse(**dto.__dict__) for dto in budget_dtos]


@router.post("/create")
async def create_internal_budget(
    budget_data: InternalBudgetCreateRequest,
    budget_use_cases: BudgetUseCases = Depends(get_budget_use_cases),
) -> InternalBudgetResponse:
    logger.bind(budget_data=budget_data).debug("Creating budget...")
    create_dto = BudgetCreateDTO(
        amount=budget_data.amount,
        period=budget_data.period,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        user_id=budget_data.user_id,
        category_id=budget_data.category_id,
    )
    budget_dto = await budget_use_cases.create_budget(budget_data=create_dto)
    logger.bind(budget=budget_dto).debug("Created budget")
    return InternalBudgetResponse(**budget_dto.__dict__)


@router.put("/update")
async def update_internal_budget(
    budget_data: InternalBudgetUpdateRequest,
    budget_use_cases: BudgetUseCases = Depends(get_budget_use_cases),
) -> InternalBudgetResponse:
    logger.bind(budget_data=budget_data).debug("Updating budget...")
    update_dto = BudgetUpdateDTO(
        id=budget_data.id,
        amount=budget_data.amount,
        period=budget_data.period,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        category_id=budget_data.category_id,
    )
    budget_dto = await budget_use_cases.update_budget(budget_data=update_dto)
    logger.bind(budget=budget_dto).debug("Updated budget")
    return InternalBudgetResponse(**budget_dto.__dict__)


@router.delete("/delete/{budget_id}")
async def delete_internal_budget(
    budget_id: UUID,
    budget_use_cases: BudgetUseCases = Depends(get_budget_use_cases),
) -> None:
    logger.bind(budget_id=budget_id).debug("Deleting budget...")
    await budget_use_cases.delete_budget(budget_id=budget_id)
    logger.bind(budget_id=budget_id).debug("Deleted budget")
    return None


@router.get("/total-amount/{user_id}")
async def get_total_budget_amount_for_period(
    user_id: UUID,
    start_date: datetime,
    end_date: datetime,
    budget_use_cases: BudgetUseCases = Depends(get_budget_use_cases),
) -> float:
    logger.bind(user_id=user_id, start_date=start_date, end_date=end_date).debug(
        "Getting total budget amount for period..."
    )
    total_amount = await budget_use_cases.get_total_budget_amount_for_period(
        user_id=user_id, start_date=start_date, end_date=end_date
    )
    logger.bind(total_amount=total_amount).debug("Got total budget amount")
    return total_amount
