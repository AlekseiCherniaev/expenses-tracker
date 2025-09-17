from datetime import datetime, timezone
from uuid import UUID

from expenses_tracker.core.constants import BudgetPeriod
from expenses_tracker.domain.entities.budget import Budget


class TestBudget:
    def test_budget_creation_success(self):
        amount = 1000.0
        period = BudgetPeriod.MONTHLY
        start_date = datetime.now(timezone.utc)
        end_date = datetime.now(timezone.utc)
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        category_id = UUID("87654321-4321-8765-4321-876543218765")

        budget = Budget(amount, period, start_date, end_date, user_id, category_id)

        assert budget.amount == amount
        assert budget.period == period
        assert budget.start_date == start_date
        assert budget.end_date == end_date
        assert budget.user_id == user_id
        assert budget.category_id == category_id
        assert isinstance(budget.id, UUID)
        assert isinstance(budget.created_at, datetime)
        assert isinstance(budget.updated_at, datetime)

    def test_budget_creation_with_default_values(self):
        amount = 500.0
        period = BudgetPeriod.WEEKLY
        start_date = datetime.now(timezone.utc)
        end_date = datetime.now(timezone.utc)
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        category_id = UUID("87654321-4321-8765-4321-876543218765")

        budget = Budget(
            amount=amount,
            period=period,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            category_id=category_id,
        )

        assert budget.amount == amount
        assert budget.period == period
        assert budget.start_date == start_date
        assert budget.end_date == end_date
        assert budget.user_id == user_id
        assert budget.category_id == category_id
        assert isinstance(budget.id, UUID)
        assert isinstance(budget.created_at, datetime)
        assert isinstance(budget.updated_at, datetime)
        assert budget.created_at <= datetime.now(timezone.utc)
        assert budget.updated_at <= datetime.now(timezone.utc)
