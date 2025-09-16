from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserUpdateRequest(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
