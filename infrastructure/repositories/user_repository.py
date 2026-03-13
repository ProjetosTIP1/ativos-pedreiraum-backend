import asyncpg
from typing import List, Optional
from uuid import UUID
from domain.entities import User
from domain.interfaces import IUserRepository

USER_COLUMNS = "id, email, full_name, role, hashed_password, created_at"


class SQLUserRepository(IUserRepository):
    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        query = f"SELECT {USER_COLUMNS} FROM users WHERE id = $1"
        row = await self.connection.fetchrow(query, user_id)
        if row:
            return User.model_validate(dict(row))
        return None

    async def get_by_email(self, email: str) -> Optional[User]:
        query = f"SELECT {USER_COLUMNS} FROM users WHERE email = $1"
        row = await self.connection.fetchrow(query, email)
        if row:
            return User.model_validate(dict(row))
        return None

    async def list_all(self) -> List[User]:
        query = f"SELECT {USER_COLUMNS} FROM users ORDER BY created_at DESC"
        rows = await self.connection.fetch(query)
        return [User.model_validate(dict(row)) for row in rows]

    async def create(self, user: User) -> User:
        user_dict = user.model_dump(exclude={"created_at"})
        columns = ", ".join(user_dict.keys())
        placeholders = ", ".join([f"${i+1}" for i in range(len(user_dict))])
        values = list(user_dict.values())

        sql = f"INSERT INTO users ({columns}) VALUES ({placeholders}) RETURNING {USER_COLUMNS}"
        row = await self.connection.fetchrow(sql, *values)
        if not row:
            raise Exception("Failed to create user")
        return User.model_validate(dict(row))

    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        if not user_data:
            return await self.get_by_id(user_id)

        user_data.pop("id", None)
        user_data.pop("created_at", None)

        set_clauses = [f"{k} = ${i+1}" for i, k in enumerate(user_data.keys())]
        values = list(user_data.values())
        
        idx = len(values) + 1
        sql = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ${idx} RETURNING {USER_COLUMNS}"
        values.append(user_id)

        row = await self.connection.fetchrow(sql, *values)
        if row:
            return User.model_validate(dict(row))
        return None

    async def delete(self, user_id: UUID) -> bool:
        query = "DELETE FROM users WHERE id = $1"
        result = await self.connection.execute(query, user_id)
        return result == "DELETE 1"
