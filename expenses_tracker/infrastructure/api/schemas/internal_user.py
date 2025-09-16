from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class InternalUserResponse(BaseModel):
    id: UUID
    username: str
    email: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class InternalUserCreateRequest(BaseModel):
    username: str
    email: EmailStr | None = None
    password: str


class InternalUserUpdateRequest(BaseModel):
    id: UUID
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None
