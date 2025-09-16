from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import dict_row

from expenses_tracker.domain.entities.category import Category
from expenses_tracker.domain.repositories.category import ICategoryRepository


class PsycopgCategoryRepository(ICategoryRepository):
    def __init__(self, conn: AsyncConnection) -> None:
        self._conn = conn

    async def get_by_id(self, category_id: UUID) -> Category | None:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                "SELECT * FROM categories WHERE id = %s", (str(category_id),)
            )
            row = await cursor.fetchone()
            return Category(**row) if row else None

    async def get_all_by_user_id(self, user_id: UUID) -> list[Category]:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                "SELECT * FROM categories WHERE user_id = %s", (str(user_id),)
            )
            rows = await cursor.fetchall()
            return [Category(**row) for row in rows]

    async def create(self, category: Category) -> Category:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                INSERT INTO categories (id, name, user_id, color, is_default, description, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(category.id),
                    category.name,
                    str(category.user_id),
                    category.color,
                    category.is_default,
                    category.description,
                    category.created_at,
                    category.updated_at,
                ),
            )
        return category

    async def update(self, category: Category) -> Category:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                UPDATE categories
                SET name        = %s,
                    color       = %s,
                    is_default  = %s,
                    description = %s,
                    updated_at  = %s
                WHERE id = %s
                """,
                (
                    category.name,
                    category.color,
                    category.is_default,
                    category.description,
                    category.updated_at,
                    str(category.id),
                ),
            )
            return category

    async def delete(self, category: Category) -> None:
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM categories WHERE id = %s", (str(category.id),)
            )
