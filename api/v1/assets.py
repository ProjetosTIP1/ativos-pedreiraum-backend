from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_session
from infrastructure.repositories.asset_repository import SQLAssetRepository
from infrastructure.repositories.category_repository import SQLCategoryRepository
from application.services.asset_service import AssetService
from domain.entities import Asset, AssetCategory

router = APIRouter(prefix="/assets", tags=["Assets"])


async def get_asset_service(
    session: AsyncSession = Depends(get_session),
) -> AssetService:
    asset_repo = SQLAssetRepository(session)
    category_repo = SQLCategoryRepository(session)
    return AssetService(asset_repo, category_repo)


@router.get("/", response_model=List[Asset])
async def list_assets(
    category: Optional[AssetCategory] = None,
    brand: Optional[str] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    q: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: AssetService = Depends(get_asset_service),
):
    return await service.get_all_assets(
        category=category,
        brand=brand,
        min_year=min_year,
        max_year=max_year,
        query_text=q,
        limit=limit,
        offset=offset,
    )


@router.get("/highlights", response_model=List[Asset])
async def get_highlights(service: AssetService = Depends(get_asset_service)):
    return await service.get_featured_assets()


@router.get("/{slug}", response_model=Asset)
async def get_asset(slug: str, service: AssetService = Depends(get_asset_service)):
    asset = await service.get_asset_by_slug(slug)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset
