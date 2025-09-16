from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from expenses_tracker.domain.entities.category import Category
from expenses_tracker.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from expenses_tracker.infrastructure.database.models.user import UserModel
    from expenses_tracker.infrastructure.database.models.expense import ExpenseModel


class CategoryModel(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["UserModel"] = relationship(back_populates="categories")
    expenses: Mapped[list["ExpenseModel"]] = relationship(
        back_populates="category", cascade="all, delete-orphan", passive_deletes=True
    )

    def to_entity(self) -> Category:
        return Category(
            id=self.id,
            name=self.name,
            user_id=self.user_id,
            color=self.color,
            is_default=self.is_default,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, category: Category) -> "CategoryModel":
        return cls(
            id=category.id,
            name=category.name,
            user_id=category.user_id,
            color=category.color,
            is_default=category.is_default,
            description=category.description,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )
