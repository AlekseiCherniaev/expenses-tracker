from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from expenses_tracker.domain.entities.user import User
from expenses_tracker.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from expenses_tracker.infrastructure.database.models.category import CategoryModel
    from expenses_tracker.infrastructure.database.models.expense import ExpenseModel
    from expenses_tracker.infrastructure.database.models.budget import BudgetModel


class UserModel(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(
        String(254), nullable=True, unique=True, index=True
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )
    last_refresh_jti: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True, default=None)

    categories: Mapped[list["CategoryModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    expenses: Mapped[list["ExpenseModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    budgets: Mapped[list["BudgetModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    def to_entity(self) -> User:
        return User(
            id=UUID(str(self.id)),
            username=self.username,
            email=self.email,
            hashed_password=self.hashed_password,
            email_verified=self.email_verified,
            last_refresh_jti=self.last_refresh_jti,
            avatar_url=self.avatar_url,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, user: User) -> "UserModel":
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            email_verified=user.email_verified,
            last_refresh_jti=user.last_refresh_jti,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
