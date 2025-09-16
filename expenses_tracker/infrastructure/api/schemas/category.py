from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    color: str
    is_default: bool
    description: str | None
    created_at: datetime
    updated_at: datetime


class CategoryCreateRequest(BaseModel):
    name: str
    description: str | None = None
    is_default: bool = False
    color: str


class CategoryUpdateRequest(BaseModel):
    id: UUID
    name: str | None = None
    description: str | None = None
    is_default: bool | None = None
    color: str | None = None
