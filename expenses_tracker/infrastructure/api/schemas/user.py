from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserUpdateRequest(BaseModel):
    email: EmailStr | None = None
    password: str | None = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str | None = None
    email_verified: bool
    created_at: datetime
    updated_at: datetime


class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr | None = None
    password: str


class InternalUserResponse(BaseModel):
    id: UUID
    username: str
    email: str | None = None
    email_verified: bool
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
    email_verified: bool | None = None
