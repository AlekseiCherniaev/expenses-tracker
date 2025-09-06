from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from expenses_tracker.core.constants import BudgetPeriod


@dataclass
class Budget:
    amount: float
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    user_id: UUID
    category_id: UUID
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)
