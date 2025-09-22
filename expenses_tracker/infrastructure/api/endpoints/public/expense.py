from datetime import datetime
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Response, status

from expenses_tracker.application.dto.expense import ExpenseCreateDTO, ExpenseUpdateDTO
from expenses_tracker.application.use_cases.expense import ExpenseUseCases
from expenses_tracker.infrastructure.api.dependencies.auth import get_current_user_id
from expenses_tracker.infrastructure.api.schemas.expense import (
    ExpenseResponse,
    ExpenseCreateRequest,
    ExpenseUpdateRequest,
)
from expenses_tracker.infrastructure.di import get_expense_use_cases

router = APIRouter(prefix="/expenses", tags=["expenses"])

logger = structlog.get_logger(__name__)


@router.get("/get/{expense_id}")
async def get_expense(
    expense_id: UUID,
    _: UUID = Depends(get_current_user_id),
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> ExpenseResponse:
    logger.bind(expense_id=expense_id).debug("Getting expense...")
    expense_dto = await expense_use_cases.get_expense(expense_id=expense_id)
    logger.bind(expense=expense_dto).debug("Got expense")
    return ExpenseResponse(**expense_dto.__dict__)


@router.get("/get-by-user")
async def get_expenses_by_user(
    user_id: UUID = Depends(get_current_user_id),
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> list[ExpenseResponse]:
    logger.bind(user_id=user_id).debug("Getting expenses for user...")
    expense_dtos = await expense_use_cases.get_expenses_by_user_id(user_id=user_id)
    logger.bind(expenses=expense_dtos).debug("Got expenses")
    return [ExpenseResponse(**dto.__dict__) for dto in expense_dtos]


@router.get("/get-by-date-range")
async def get_expenses_by_date_range(
    start_date: datetime,
    end_date: datetime,
    user_id: UUID = Depends(get_current_user_id),
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> list[ExpenseResponse]:
    logger.bind(user_id=user_id, start_date=start_date, end_date=end_date).debug(
        "Getting expenses by date range..."
    )
    expense_dtos = await expense_use_cases.get_expenses_by_user_id_and_date_range(
        user_id=user_id, start_date=start_date, end_date=end_date
    )
    logger.bind(expenses=expense_dtos).debug("Got expenses by date range")
    return [ExpenseResponse(**dto.__dict__) for dto in expense_dtos]


@router.get("/get-by-category/{category_id}")
async def get_expenses_by_category(
    category_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> list[ExpenseResponse]:
    logger.bind(user_id=user_id, category_id=category_id).debug(
        "Getting expenses by category..."
    )
    expense_dtos = await expense_use_cases.get_expenses_by_user_id_and_category_id(
        user_id=user_id, category_id=category_id
    )
    logger.bind(expenses=expense_dtos).debug("Got expenses by category")
    return [ExpenseResponse(**dto.__dict__) for dto in expense_dtos]


@router.post("/create")
async def create_expense(
    expense_data: ExpenseCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> ExpenseResponse:
    logger.bind(expense_data=expense_data).debug("Creating expense...")
    create_dto = ExpenseCreateDTO(
        user_id=user_id,
        amount=expense_data.amount,
        date=expense_data.date,
        category_id=expense_data.category_id,
        description=expense_data.description,
    )
    expense_dto = await expense_use_cases.create_expense(expense_data=create_dto)
    logger.bind(expense=expense_dto).debug("Created expense")
    return ExpenseResponse(**expense_dto.__dict__)


@router.put("/update")
async def update_expense(
    expense_data: ExpenseUpdateRequest,
    _: UUID = Depends(get_current_user_id),
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> ExpenseResponse:
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
    return ExpenseResponse(**expense_dto.__dict__)


@router.delete("/delete/{expense_id}")
async def delete_expense(
    expense_id: UUID,
    _: UUID = Depends(get_current_user_id),
    expense_use_cases: ExpenseUseCases = Depends(get_expense_use_cases),
) -> Response:
    logger.bind(expense_id=expense_id).debug("Deleting expense...")
    await expense_use_cases.delete_expense(expense_id=expense_id)
    logger.bind(expense_id=expense_id).debug("Deleted expense")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
