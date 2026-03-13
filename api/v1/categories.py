from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_session
from infrastructure.repositories.category_repository import SQLCategoryRepository
from application.services.category_service import CategoryService
from domain.entities import Category

router = APIRouter(prefix="/categories", tags=["Categories"])


async def get_category_service(
    session: AsyncSession = Depends(get_session),
) -> CategoryService:
    repo = SQLCategoryRepository(session)
    return CategoryService(repo)


@router.get("/", response_model=List[Category])
async def list_categories(service: CategoryService = Depends(get_category_service)):
    return await service.get_all_categories()
