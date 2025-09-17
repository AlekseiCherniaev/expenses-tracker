from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import partial
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
    created_at: datetime = field(default_factory=partial(datetime.now, timezone.utc))
    updated_at: datetime = field(default_factory=partial(datetime.now, timezone.utc))
    id: UUID = field(default_factory=uuid4)
