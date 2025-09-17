from datetime import datetime
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Query

from expenses_tracker.application.dto.expense import (
    ExpenseCreateDTO,
    ExpenseUpdateDTO,
)
from expenses_tracker.application.use_cases.expense import ExpenseUseCases
from expenses_tracker.infrastructure.api.schemas.expense import (
    InternalExpenseCreateRequest,
    InternalExpenseResponse,
    InternalExpenseUpdateRequest,
)
from expenses_tracker.infrastructure.di import get_expense_use_cases

router = APIRouter(prefix="/expenses", tags=["internal expenses"])

logger = structlog.get_logger(__name__)


@router.get("/get/{expense_id}")
async def get_internal_expense(
    expense_id: UUID,
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> InternalExpenseResponse:
    logger.bind(expense_id=expense_id).debug("Getting expense...")
    expense_dto = await expense_use_cases.get_expense(expense_id=expense_id)
    logger.bind(expense=expense_dto).debug("Got expense")
    return InternalExpenseResponse(**expense_dto.__dict__)


@router.get("/get-by-user/{user_id}")
async def get_internal_expenses_by_user(
    user_id: UUID,
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> list[InternalExpenseResponse]:
    logger.bind(user_id=user_id).debug("Getting expenses for user...")
    expense_dtos = await expense_use_cases.get_expenses_by_user_id(user_id=user_id)
    logger.bind(expenses=expense_dtos).debug("Got expenses")
    return [InternalExpenseResponse(**dto.__dict__) for dto in expense_dtos]


@router.get("/get-by-user-date-range/{user_id}")
async def get_internal_expenses_by_user_and_date_range(
    user_id: UUID,
    start_date: datetime = Query(..., description="Start date for filtering"),
    end_date: datetime = Query(..., description="End date for filtering"),
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> list[InternalExpenseResponse]:
    logger.bind(user_id=user_id, start_date=start_date, end_date=end_date).debug(
        "Getting expenses for user by date range..."
    )
    expense_dtos = await expense_use_cases.get_expenses_by_user_id_and_date_range(
        user_id=user_id, start_date=start_date, end_date=end_date
    )
    logger.bind(expenses=expense_dtos).debug("Got expenses by date range")
    return [InternalExpenseResponse(**dto.__dict__) for dto in expense_dtos]


@router.get("/get-by-user-category/{user_id}/{category_id}")
async def get_internal_expenses_by_user_and_category(
    user_id: UUID,
    category_id: UUID,
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> list[InternalExpenseResponse]:
    logger.bind(user_id=user_id, category_id=category_id).debug(
        "Getting expenses for user by category..."
    )
    expense_dtos = await expense_use_cases.get_expenses_by_user_id_and_category_id(
        user_id=user_id, category_id=category_id
    )
    logger.bind(expenses=expense_dtos).debug("Got expenses by category")
    return [InternalExpenseResponse(**dto.__dict__) for dto in expense_dtos]


@router.post("/create")
async def create_internal_expense(
    expense_data: InternalExpenseCreateRequest,
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> InternalExpenseResponse:
    logger.bind(expense_data=expense_data).debug("Creating expense...")
    create_dto = ExpenseCreateDTO(
        amount=expense_data.amount,
        date=expense_data.date,
        user_id=expense_data.user_id,
        category_id=expense_data.category_id,
        description=expense_data.description,
    )
    expense_dto = await expense_use_cases.create_expense(expense_data=create_dto)
    logger.bind(expense=expense_dto).debug("Created expense")
    return InternalExpenseResponse(**expense_dto.__dict__)


@router.put("/update")
async def update_internal_expense(
    expense_data: InternalExpenseUpdateRequest,
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> InternalExpenseResponse:
    logger.bind(expense_data=expense_data).debug("Updating expense...")
    update_dto = ExpenseUpdateDTO(
        id=expense_data.id,
        amount=expense_data.amount,
        date=expense_data.date,
        category_id=expense_data.category_id,
        description=expense_data.description,
    )
    expense_dto = await expense_use_cases.update_expense(expense_data=update_dto)
    logger.bind(expense=expense_dto).debug("Updated expense")
    return InternalExpenseResponse(**expense_dto.__dict__)


@router.delete("/delete/{expense_id}")
async def delete_internal_expense(
    expense_id: UUID,
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> None:
    logger.bind(expense_id=expense_id).debug("Deleting expense...")
    await expense_use_cases.delete_expense(expense_id=expense_id)
    logger.bind(expense_id=expense_id).debug("Deleted expense")
    return None
