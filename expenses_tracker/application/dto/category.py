from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CategoryDTO:
    id: UUID
    user_id: UUID
    name: str
    color: str
    is_default: bool
    description: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class CategoryCreateDTO:
    name: str
    user_id: UUID
    color: str
    is_default: bool
    description: str | None


@dataclass
class CategoryUpdateDTO:
    id: UUID
    name: str | None = None
    color: str | None = None
    is_default: bool | None = None
    description: str | None = None
