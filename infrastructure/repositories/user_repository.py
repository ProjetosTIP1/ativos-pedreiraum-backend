import asyncpg
from typing import List, Optional
from uuid import UUID
from domain.entities import User
from domain.interfaces import IUserRepository
from core.helpers.logger_helper import logger

USER_COLUMNS = "id, email, full_name, role, hashed_password, created_at"


class SQLUserRepository(IUserRepository):
    def __init__(self, connection: asyncpg.Connection):
        try:
            self.connection = connection
        except Exception as e:
            logger.error(f"Error initializing SQLUserRepository: {e}")
            raise

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        try:
            query = f"SELECT {USER_COLUMNS} FROM users WHERE id = $1"
            row = await self.connection.fetchrow(query, user_id)
            if row:
                return User.model_validate(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error fetching user by ID {user_id}: {e}")
            raise

    async def get_by_email(self, email: str) -> Optional[User]:
        try:
            query = f"SELECT {USER_COLUMNS} FROM users WHERE email = $1"
            row = await self.connection.fetchrow(query, email)
            if row:
                return User.model_validate(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            raise

    async def list_all(self) -> List[User]:
        try:
            query = f"SELECT {USER_COLUMNS} FROM users ORDER BY created_at DESC"
            rows = await self.connection.fetch(query)
            return [User.model_validate(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise

    async def create(self, user: User) -> User:
        try:
            user_dict = user.model_dump(exclude={"created_at"})
            columns = ", ".join(user_dict.keys())
            placeholders = ", ".join([f"${i + 1}" for i in range(len(user_dict))])
            values = list(user_dict.values())

            sql = f"INSERT INTO users ({columns}) VALUES ({placeholders}) RETURNING {USER_COLUMNS}"
            row = await self.connection.fetchrow(sql, *values)
            if not row:
                raise Exception("Failed to create user")
            return User.model_validate(dict(row))
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        try:
            if not user_data:
                return await self.get_by_id(user_id)

            user_data.pop("id", None)
            user_data.pop("created_at", None)

            set_clauses = [f"{k} = ${i + 1}" for i, k in enumerate(user_data.keys())]
            values = list(user_data.values())

            idx = len(values) + 1
            sql = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ${idx} RETURNING {USER_COLUMNS}"
            values.append(user_id)

            row = await self.connection.fetchrow(sql, *values)
            if row:
                return User.model_validate(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    async def delete(self, user_id: UUID) -> bool:
        try:
            query = "DELETE FROM users WHERE id = $1"
            result = await self.connection.execute(query, user_id)
            return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise
