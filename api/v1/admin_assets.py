from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from api.v1.auth import get_current_user, get_current_admin
from api.v1.assets import get_asset_service
from application.services.asset_service import AssetService
from domain.entities import Asset, CreateAssetRequest, UpdateAssetRequest, User
from core.helpers.exceptions_helper import ServiceException, to_http_exception

router = APIRouter(prefix="/admin/assets", tags=["Admin Assets"])


@router.post("/", response_model=Asset, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: CreateAssetRequest,
    current_user: User = Depends(get_current_user),
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


@router.patch("/{asset_id}", response_model=Asset)
async def update_asset(
    asset_id: UUID,
    asset_data: UpdateAssetRequest,
    _current_user: User = Depends(get_current_user),
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
