from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ExpenseDTO:
    id: UUID
    amount: float
    date: datetime
    user_id: UUID
    category_id: UUID
    description: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class ExpenseCreateDTO:
    amount: float
    date: datetime
    user_id: UUID
    category_id: UUID
    description: str | None


@dataclass
class ExpenseUpdateDTO:
    id: UUID
    amount: float | None = None
    date: datetime | None = None
    category_id: UUID | None = None
    description: str | None = None
