import asyncpg
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from api.v1.auth import get_current_admin
from api.v1.assets import get_asset_service
from core.database import get_db_connection
from infrastructure.repositories.asset_repository import SQLAssetRepository
from application.services.asset_service import AssetService
from application.services.asset_approval_service import AssetApprovalService
from domain.entities import Asset, User

router = APIRouter(prefix="/admin/assets", tags=["Admin Assets"])


async def get_approval_service(
    conn: asyncpg.Connection = Depends(get_db_connection),
) -> AssetApprovalService:
    repo = SQLAssetRepository(conn)
    return AssetApprovalService(repo)


@router.post("/", response_model=Asset, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: dict,
    current_user: User = Depends(get_current_admin),
    service: AssetService = Depends(get_asset_service),
):
    try:
        # Admin can create assets directly, we set user_id for tracking
        return await service.create_asset(asset_data, user_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{asset_id}/approve", response_model=Asset)
async def approve_asset(
    asset_id: UUID,
    approval_data: dict = {},
    _current_admin: User = Depends(get_current_admin),
    service: AssetApprovalService = Depends(get_approval_service),
):
    try:
        asset = await service.approve_asset(asset_id, approval_data)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{asset_id}/reject", response_model=Asset)
async def reject_asset(
    asset_id: UUID,
    _current_admin: User = Depends(get_current_admin),
    service: AssetApprovalService = Depends(get_approval_service),
):
    try:
        asset = await service.reject_asset(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{asset_id}", response_model=Asset)
async def update_asset(
    asset_id: UUID,
    asset_data: dict,
    _current_admin: User = Depends(get_current_admin),
    service: AssetService = Depends(get_asset_service),
):
    asset = await service.update_asset(asset_id, asset_data)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


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
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
