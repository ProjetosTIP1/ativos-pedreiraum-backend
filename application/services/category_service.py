from typing import List
from domain.entities import Category
from domain.interfaces import ICategoryRepository


class CategoryService:
    def __init__(self, category_repo: ICategoryRepository):
        self.category_repo = category_repo

    async def get_all_categories(self) -> List[Category]:
        return await self.category_repo.list_all()
