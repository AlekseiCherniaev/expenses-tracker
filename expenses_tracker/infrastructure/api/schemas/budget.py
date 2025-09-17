from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from expenses_tracker.core.constants import BudgetPeriod


class BudgetResponse(BaseModel):
    id: UUID
    amount: float
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    user_id: UUID
    category_id: UUID
    created_at: datetime
    updated_at: datetime


class BudgetCreateRequest(BaseModel):
    amount: float
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    category_id: UUID


class BudgetUpdateRequest(BaseModel):
    id: UUID
    amount: float | None = None
    period: BudgetPeriod | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    category_id: UUID | None = None


class InternalBudgetResponse(BaseModel):
    id: UUID
    amount: float
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    user_id: UUID
    category_id: UUID
    created_at: datetime
    updated_at: datetime


class InternalBudgetCreateRequest(BaseModel):
    amount: float
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    user_id: UUID
    category_id: UUID


class InternalBudgetUpdateRequest(BaseModel):
    id: UUID
    amount: float | None = None
    period: BudgetPeriod | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    category_id: UUID | None = None
