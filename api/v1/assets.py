from uuid import UUID
import asyncpg
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from core.database import get_db_connection
from infrastructure.repositories.asset_repository import SQLAssetRepository
from infrastructure.repositories.category_repository import SQLCategoryRepository
from infrastructure.repositories.image_repository import SQLImageRepository
from application.services.image_service import ImageService
from application.services.asset_service import AssetService
from domain.entities import Asset
from domain.enums import AssetCategory
from core.helpers.exceptions_helper import ServiceException, to_http_exception

router = APIRouter(prefix="/assets", tags=["Assets"])


async def get_asset_service(
    conn: asyncpg.Connection = Depends(get_db_connection),
) -> AssetService:
    asset_repo = SQLAssetRepository(conn)
    category_repo = SQLCategoryRepository(conn)
    image_repo = SQLImageRepository(conn)
    image_service = ImageService(image_repo)
    return AssetService(asset_repo, category_repo, image_service)


@router.get("/", response_model=List[Asset])
async def list_assets(
    category: Optional[AssetCategory] = None,
    brand: Optional[str] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    q: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: Optional[UUID] = None,
    service: AssetService = Depends(get_asset_service),
):
    try:
        return await service.get_available_assets(
            category=category,
            brand=brand,
            min_year=min_year,
            max_year=max_year,
            limit=limit,
            offset=offset,
            user_id=user_id,
        )
    except HTTPException:
        raise
    except ServiceException as e:
        raise to_http_exception(e)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/highlights", response_model=List[Asset])
async def get_highlights(service: AssetService = Depends(get_asset_service)):
    try:
        return await service.get_featured_assets()
    except HTTPException:
        raise
    except ServiceException as e:
        raise to_http_exception(e)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{id}", response_model=Asset)
async def get_asset(id: str, service: AssetService = Depends(get_asset_service)):
    try:
        asset = await service.get_asset_by_id(id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return asset
    except HTTPException:
        raise
    except ServiceException as e:
        raise to_http_exception(e)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
