from datetime import datetime, timezone
from uuid import UUID

from expenses_tracker.domain.entities.expense import Expense


class TestExpense:
    def test_expense_creation_success(self):
        amount = 100.50
        date = datetime.now(timezone.utc)
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        category_id = UUID("87654321-4321-8765-4321-876543218765")
        description = "Groceries shopping"

        expense = Expense(amount, date, user_id, category_id, description)

        assert expense.amount == amount
        assert expense.date == date
        assert expense.user_id == user_id
        assert expense.category_id == category_id
        assert expense.description == description
        assert isinstance(expense.id, UUID)
        assert isinstance(expense.created_at, datetime)
        assert isinstance(expense.updated_at, datetime)
        assert expense.created_at.tzinfo == timezone.utc
        assert expense.updated_at.tzinfo == timezone.utc
