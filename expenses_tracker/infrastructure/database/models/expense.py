from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from expenses_tracker.domain.entities.expense import Expense
from expenses_tracker.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from expenses_tracker.infrastructure.database.models.user import UserModel
    from expenses_tracker.infrastructure.database.models.category import CategoryModel


class ExpenseModel(Base):
    __tablename__ = "expenses"

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["UserModel"] = relationship(back_populates="expenses")

    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped["CategoryModel"] = relationship(back_populates="expenses")

    def to_entity(self) -> Expense:
        return Expense(
            id=self.id,
            amount=self.amount,
            date=self.date,
            user_id=self.user_id,
            category_id=self.category_id,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, expense: Expense) -> "ExpenseModel":
        return cls(
            id=expense.id,
            amount=expense.amount,
            date=expense.date,
            user_id=expense.user_id,
            category_id=expense.category_id,
            description=expense.description,
            created_at=expense.created_at,
            updated_at=expense.updated_at,
        )
