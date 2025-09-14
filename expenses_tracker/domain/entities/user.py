from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import partial
from uuid import UUID, uuid4


@dataclass
class User:
    username: str
    hashed_password: str
    email: str | None = None
    is_active: bool = False
    created_at: datetime = field(default_factory=partial(datetime.now, timezone.utc))
    updated_at: datetime = field(default_factory=partial(datetime.now, timezone.utc))
    id: UUID = field(default_factory=uuid4)
