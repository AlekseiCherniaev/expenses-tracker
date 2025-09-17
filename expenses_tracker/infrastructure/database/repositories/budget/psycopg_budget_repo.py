from datetime import datetime
from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import dict_row

from expenses_tracker.core.constants import BudgetPeriod
from expenses_tracker.domain.entities.budget import Budget
from expenses_tracker.domain.repositories.budget import IBudgetRepository


class PsycopgBudgetRepository(IBudgetRepository):
    def __init__(self, conn: AsyncConnection) -> None:
        self._conn = conn

    @staticmethod
    def _row_to_budget(row: dict) -> Budget:  # type: ignore
        return Budget(
            **{
                **row,
                "period": BudgetPeriod(row["period"]),
            }
        )

    async def get_by_id(self, budget_id: UUID) -> Budget | None:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                "SELECT * FROM budgets WHERE id = %s", (str(budget_id),)
            )
            row = await cursor.fetchone()
            return self._row_to_budget(row) if row else None

    async def get_all_by_user_id(self, user_id: UUID) -> list[Budget]:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                "SELECT * FROM budgets WHERE user_id = %s", (str(user_id),)
            )
            rows = await cursor.fetchall()
            return [self._row_to_budget(r) for r in rows]

    async def get_by_user_id_and_date_range(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[Budget]:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                SELECT * FROM budgets 
                WHERE user_id = %s 
                AND start_date >= %s 
                AND end_date <= %s
                """,
                (str(user_id), start_date, end_date),
            )
            rows = await cursor.fetchall()
            return [self._row_to_budget(r) for r in rows]

    async def get_by_user_id_and_category_id(
        self, user_id: UUID, category_id: UUID
    ) -> list[Budget]:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                SELECT * FROM budgets 
                WHERE user_id = %s 
                AND category_id = %s
                """,
                (str(user_id), str(category_id)),
            )
            rows = await cursor.fetchall()
            return [self._row_to_budget(r) for r in rows]

    async def get_active_budgets_by_user_id(
        self, user_id: UUID, current_date: datetime
    ) -> list[Budget]:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                SELECT * FROM budgets 
                WHERE user_id = %s 
                AND start_date <= %s 
                AND end_date >= %s
                """,
                (str(user_id), current_date, current_date),
            )
            rows = await cursor.fetchall()
            return [self._row_to_budget(r) for r in rows]

    async def get_by_user_id_and_period(
        self, user_id: UUID, period: BudgetPeriod
    ) -> list[Budget]:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                SELECT * FROM budgets 
                WHERE user_id = %s 
                AND period = %s
                """,
                (str(user_id), period.value),
            )
            rows = await cursor.fetchall()
            return [self._row_to_budget(r) for r in rows]

    async def create(self, budget: Budget) -> Budget:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                INSERT INTO budgets 
                (id, amount, period, start_date, end_date, user_id, category_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(budget.id),
                    budget.amount,
                    budget.period.value,
                    budget.start_date,
                    budget.end_date,
                    str(budget.user_id),
                    str(budget.category_id),
                    budget.created_at,
                    budget.updated_at,
                ),
            )
        return budget

    async def update(self, budget: Budget) -> Budget:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                UPDATE budgets
                SET amount = %s,
                    period = %s,
                    start_date = %s,
                    end_date = %s,
                    category_id = %s,
                    updated_at = %s
                WHERE id = %s
                """,
                (
                    budget.amount,
                    budget.period.value,
                    budget.start_date,
                    budget.end_date,
                    str(budget.category_id),
                    budget.updated_at,
                    str(budget.id),
                ),
            )
        return budget

    async def delete(self, budget: Budget) -> None:
        async with self._conn.cursor() as cursor:
            await cursor.execute("DELETE FROM budgets WHERE id = %s", (str(budget.id),))

    async def get_total_budget_amount_for_period(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> float:
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT COALESCE(SUM(amount), 0) as total_amount
                FROM budgets 
                WHERE user_id = %s 
                AND start_date >= %s 
                AND end_date <= %s
                """,
                (str(user_id), start_date, end_date),
            )
            result = await cursor.fetchone()
            return result[0] if result else 0.0
