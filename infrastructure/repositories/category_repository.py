import asyncpg
from typing import List, Optional
from domain.entities import Category
from domain.interfaces import ICategoryRepository
from core.helpers.logger_helper import logger


class SQLCategoryRepository(ICategoryRepository):
    def __init__(self, connection: asyncpg.Connection):
        try:
            self.connection = connection
        except Exception as e:
            logger.error(f"Error initializing SQLCategoryRepository: {e}")
            raise

    async def list_all(self) -> List[Category]:
        try:
            query = """SELECT id,
            name,
            created_at
            FROM categories ORDER BY name"""
            rows = await self.connection.fetch(query)
            return [Category.model_validate(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error listing categories: {e}")
            raise

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        try:
            query = """SELECT id,
            name,
            created_at
            FROM categories WHERE id = $1"""
            row = await self.connection.fetchrow(query, category_id)
            if row:
                return Category.model_validate(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error fetching category by ID {category_id}: {e}")
            raise
