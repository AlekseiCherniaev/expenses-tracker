from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean
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
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

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
            id=self.id,
            username=self.username,
            email=self.email,
            hashed_password=self.hashed_password,
            is_active=self.is_active,
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
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
