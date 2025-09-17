from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from expenses_tracker.core.constants import BudgetPeriod
from expenses_tracker.domain.entities.budget import Budget
from expenses_tracker.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from expenses_tracker.infrastructure.database.models.user import UserModel
    from expenses_tracker.infrastructure.database.models.category import CategoryModel


class BudgetModel(Base):
    __tablename__ = "budgets"

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    period: Mapped[BudgetPeriod] = mapped_column(Enum(BudgetPeriod), nullable=False)
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["UserModel"] = relationship(back_populates="budgets")
    category: Mapped["CategoryModel"] = relationship(back_populates="budgets")

    def to_entity(self) -> Budget:
        return Budget(
            id=self.id,
            amount=self.amount,
            period=self.period,
            start_date=self.start_date,
            end_date=self.end_date,
            user_id=self.user_id,
            category_id=self.category_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, budget: Budget) -> "BudgetModel":
        return cls(
            id=budget.id,
            amount=budget.amount,
            period=budget.period,
            start_date=budget.start_date,
            end_date=budget.end_date,
            user_id=budget.user_id,
            category_id=budget.category_id,
            created_at=budget.created_at,
            updated_at=budget.updated_at,
        )
