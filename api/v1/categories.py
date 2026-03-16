import asyncpg
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from core.database import get_db_connection
from infrastructure.repositories.category_repository import SQLCategoryRepository
from application.services.category_service import CategoryService
from domain.entities import Category
from core.helpers.exceptions_helper import ServiceException, to_http_exception

router = APIRouter(prefix="/categories", tags=["Categories"])


async def get_category_service(
    conn: asyncpg.Connection = Depends(get_db_connection),
) -> CategoryService:
    repo = SQLCategoryRepository(conn)
    return CategoryService(repo)


@router.get("/", response_model=List[Category])
async def list_categories(service: CategoryService = Depends(get_category_service)):
    try:
        return await service.get_all_categories()
    except HTTPException:
        raise
    except ServiceException as e:
        raise to_http_exception(e)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
