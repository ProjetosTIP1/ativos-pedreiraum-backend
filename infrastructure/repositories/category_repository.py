from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from domain.entities import Category
from domain.interfaces import ICategoryRepository


class SQLCategoryRepository(ICategoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self) -> List[Category]:
        query = text("SELECT * FROM categories ORDER BY name")
        result = await self.session.execute(query)
        return [Category.model_validate(dict(row)) for row in result.mappings().all()]

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        query = text("SELECT * FROM categories WHERE id = :id")
        result = await self.session.execute(query, {"id": category_id})
        row = result.mappings().first()
        if row:
            return Category.model_validate(dict(row))
        return None
