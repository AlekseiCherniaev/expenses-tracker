from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InternalExpenseResponse(BaseModel):
    id: UUID
    amount: float
    date: datetime
    user_id: UUID
    category_id: UUID
    description: str | None
    created_at: datetime
    updated_at: datetime


class InternalExpenseCreateRequest(BaseModel):
    amount: float
    date: datetime
    user_id: UUID
    category_id: UUID
    description: str | None = None


class InternalExpenseUpdateRequest(BaseModel):
    id: UUID
    amount: float | None = None
    date: datetime | None = None
    category_id: UUID | None = None
    description: str | None = None


class ExpenseResponse(BaseModel):
    id: UUID
    amount: float
    date: datetime
    category_id: UUID
    description: str | None
    created_at: datetime
    updated_at: datetime


class ExpenseCreateRequest(BaseModel):
    amount: float
    date: datetime
    category_id: UUID
    description: str | None = None


class ExpenseUpdateRequest(BaseModel):
    id: UUID
    amount: float | None = None
    date: datetime | None = None
    category_id: UUID | None = None
    description: str | None = None
