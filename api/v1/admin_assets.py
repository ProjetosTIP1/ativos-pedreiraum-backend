from domain.enums import AssetStatus, AssetCategory
from fastapi import Query
from typing import Optional
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from api.v1.auth import get_current_admin
from api.v1.assets import get_asset_service
from application.services.asset_service import AssetService
from domain.entities import Asset, CreateAssetRequest, UpdateAssetRequest, User
from core.helpers.exceptions_helper import ServiceException, to_http_exception

router = APIRouter(prefix="/admin/assets", tags=["Admin Assets"])


@router.post("/", response_model=Asset, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: CreateAssetRequest,
    current_user: User = Depends(get_current_admin),
    service: AssetService = Depends(get_asset_service),
):
    try:
        # Admin can create assets directly, we set user_id for tracking
        return await service.create_asset(asset_data, user_id=current_user.id)
    except HTTPException:
        raise
    except ServiceException as e:
        raise to_http_exception(e)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[Asset])
async def list_assets(
    service: AssetService = Depends(get_asset_service),
    current_user: User = Depends(get_current_admin),
    category: Optional[AssetCategory] = None,
    brand: Optional[str] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    status: Optional[AssetStatus] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: Optional[UUID] = None,
):
    try:
        return await service.get_all_assets(
            category=category,
            brand=brand,
            min_year=min_year,
            max_year=max_year,
            status=status,
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


@router.patch("/{asset_id}", response_model=Asset)
async def update_asset(
    asset_id: UUID,
    asset_data: UpdateAssetRequest,
    _current_admin: User = Depends(get_current_admin),
    service: AssetService = Depends(get_asset_service),
):
    try:
        asset = await service.update_asset(asset_id, asset_data)
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


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: UUID,
    _current_admin: User = Depends(get_current_admin),
    service: AssetService = Depends(get_asset_service),
):
    try:
        success = await service.delete_asset(asset_id)
        if not success:
            raise HTTPException(status_code=404, detail="Asset not found")
        return {"message": "Asset deleted successfully"}
    except HTTPException:
        raise
    except ServiceException as e:
        raise to_http_exception(e)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
