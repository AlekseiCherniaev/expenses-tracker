from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import dict_row

from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.repositories.user import IUserRepository


class PsycopgUserRepository(IUserRepository):
    def __init__(self, conn: AsyncConnection) -> None:
        self._conn = conn

    async def get_by_id(self, user_id: UUID) -> User | None:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("SELECT * FROM users WHERE id = %s", (str(user_id),))
            row = await cursor.fetchone()
            return User(**row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = await cursor.fetchone()
            return User(**row) if row else None

    async def get_by_username(self, username: str) -> User | None:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            row = await cursor.fetchone()
            return User(**row) if row else None

    async def get_all(self) -> list[User]:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("SELECT * FROM users")
            rows = await cursor.fetchall()
            return [User(**row) for row in rows]

    async def create(self, user: User) -> User:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                INSERT INTO users (id, email, username, hashed_password, email_verified, last_refresh_jti, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(user.id),
                    user.email,
                    user.username,
                    user.hashed_password,
                    user.email_verified,
                    user.last_refresh_jti,
                    user.created_at,
                    user.updated_at,
                ),
            )
        return user

    async def update(self, user: User) -> User:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """
                UPDATE users
                SET username        = %s,
                    email           = %s,
                    hashed_password = %s,
                    email_verified       = %s,
                    updated_at      = %s,
                    last_refresh_jti= %s
                WHERE id = %s
                """,
                (
                    user.username,
                    user.email,
                    user.hashed_password,
                    user.email_verified,
                    user.updated_at,
                    user.last_refresh_jti,
                    str(user.id),
                ),
            )
            return user

    async def update_last_refresh_jti(self, user_id: UUID, jti: str | None) -> None:
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE users
                SET last_refresh_jti = %s,
                    updated_at       = NOW()
                WHERE id = %s
                """,
                (jti, str(user_id)),
            )

    async def get_for_update(self, user_id: UUID) -> User | None:
        async with self._conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                "SELECT * FROM users WHERE id = %s FOR UPDATE",
                (str(user_id),),
            )
            row = await cursor.fetchone()
            return User(**row) if row else None

    async def delete(self, user: User) -> None:
        async with self._conn.cursor() as cur:
            await cur.execute("DELETE FROM users WHERE id = %s", (str(user.id),))
