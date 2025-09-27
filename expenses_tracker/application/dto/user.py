from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class UserDTO:
    id: UUID
    username: str
    email: str | None
    email_verified: bool
    last_refresh_jti: str | None
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class UserCreateDTO:
    username: str
    email: str | None
    password: str


@dataclass
class UserUpdateDTO:
    id: UUID
    email: str | None = None
    password: str | None = None
    email_verified: bool | None = None
    avatar_url: bool | None = None
