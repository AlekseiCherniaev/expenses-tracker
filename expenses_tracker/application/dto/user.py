from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class UserDTO:
    id: UUID
    username: str
    email: str | None
    is_active: bool
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
    is_active: bool | None = None
