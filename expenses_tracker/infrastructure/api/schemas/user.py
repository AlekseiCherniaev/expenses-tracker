from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: UUID
    email: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr | None = None
    password: str


class UserUpdateRequest(BaseModel):
    id: UUID
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None
