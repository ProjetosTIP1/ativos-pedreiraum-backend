import asyncpg
from typing import List, Optional
from domain.entities import Category
from domain.interfaces import ICategoryRepository

CATEGORY_COLUMNS = "id, name, slug, parent_id"


class SQLCategoryRepository(ICategoryRepository):
    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection

    async def list_all(self) -> List[Category]:
        query = f"SELECT {CATEGORY_COLUMNS} FROM categories ORDER BY name"
        rows = await self.connection.fetch(query)
        return [Category.model_validate(dict(row)) for row in rows]

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        query = f"SELECT {CATEGORY_COLUMNS} FROM categories WHERE id = $1"
        row = await self.connection.fetchrow(query, category_id)
        if row:
            return Category.model_validate(dict(row))
        return None
