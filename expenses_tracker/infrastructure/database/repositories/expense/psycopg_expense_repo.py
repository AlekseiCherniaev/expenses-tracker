from datetime import datetime
from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import dict_row

from expenses_tracker.domain.entities.expense import Expense
from expenses_tracker.domain.repositories.expense import IExpenseRepository


class PsycopgExpenseRepository(IExpenseRepository):
    def __init__(self, conn: AsyncConnection) -> None:
        self._conn = conn

    async def get_by_id(self, expense_id: UUID) -> Expense | None:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                "SELECT * FROM expenses WHERE id = %s", (str(expense_id),)
            )
            row = await cursor.fetchone()
            return Expense(**row) if row else None

    async def get_all_by_user_id(self, user_id: UUID) -> list[Expense]:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                "SELECT * FROM expenses WHERE user_id = %s", (str(user_id),)
            )
            rows = await cursor.fetchall()
            return [Expense(**row) for row in rows]

    async def get_by_user_id_and_date_range(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[Expense]:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                "SELECT * FROM expenses WHERE user_id = %s AND date BETWEEN %s AND %s",
                (str(user_id), start_date, end_date),
            )
            rows = await cursor.fetchall()
            return [Expense(**row) for row in rows]

    async def get_by_user_id_and_category_id(
        self, user_id: UUID, category_id: UUID
    ) -> list[Expense]:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                "SELECT * FROM expenses WHERE user_id = %s AND category_id = %s",
                (str(user_id), str(category_id)),
            )
            rows = await cursor.fetchall()
            return [Expense(**row) for row in rows]

    async def create(self, expense: Expense) -> Expense:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                INSERT INTO expenses (id, amount, date, user_id, category_id, description, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(expense.id),
                    expense.amount,
                    expense.date,
                    str(expense.user_id),
                    str(expense.category_id),
                    expense.description,
                    expense.created_at,
                    expense.updated_at,
                ),
            )
        return expense

    async def update(self, expense: Expense) -> Expense:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                UPDATE expenses
                SET amount      = %s,
                    date        = %s,
                    category_id = %s,
                    description = %s,
                    updated_at  = %s
                WHERE id = %s
                """,
                (
                    expense.amount,
                    expense.date,
                    str(expense.category_id),
                    expense.description,
                    expense.updated_at,
                    str(expense.id),
                ),
            )
            return expense

    async def delete(self, expense: Expense) -> None:
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM expenses WHERE id = %s", (str(expense.id),)
            )
