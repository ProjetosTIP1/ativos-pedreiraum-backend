from typing import List
from domain.entities import Category
from domain.interfaces import ICategoryRepository
from core.helpers.exceptions_helper import ServiceException, InfrastructureServiceException


class CategoryService:
    def __init__(self, category_repo: ICategoryRepository):
        try:
            self.category_repo = category_repo
        except Exception as e:
            raise InfrastructureServiceException("Failed to initialize category service") from e

    async def get_all_categories(self) -> List[Category]:
        try:
            return await self.category_repo.list_all()
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to list categories") from e
