from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Expense:
    amount: float
    date: datetime
    user_id: UUID
    category_id: UUID
    description: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)
