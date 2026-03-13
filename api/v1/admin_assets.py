from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from api.v1.auth import get_current_user
from api.v1.assets import get_asset_service
from application.services.asset_service import AssetService
from domain.entities import Asset

router = APIRouter(prefix="/admin/assets", tags=["Admin Assets"])


@router.post("/", response_model=Asset, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: dict,
    _current_user: str = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    try:
        return await service.create_asset(asset_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{asset_id}", response_model=Asset)
async def update_asset(
    asset_id: UUID,
    asset_data: dict,
    _current_user: str = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    asset = await service.update_asset(asset_id, asset_data)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: UUID,
    _current_user: str = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    try:
        success = await service.delete_asset(asset_id)
        if not success:
            raise HTTPException(status_code=404, detail="Asset not found")
        return {"message": "Asset deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
