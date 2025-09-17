from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from expenses_tracker.core.constants import BudgetPeriod


@dataclass
class BudgetDTO:
    id: UUID
    amount: float
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    user_id: UUID
    category_id: UUID
    created_at: datetime
    updated_at: datetime


@dataclass
class BudgetCreateDTO:
    amount: float
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    user_id: UUID
    category_id: UUID


@dataclass
class BudgetUpdateDTO:
    id: UUID
    amount: float | None = None
    period: BudgetPeriod | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    category_id: UUID | None = None
