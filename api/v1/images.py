import asyncpg
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from core.database import get_db_connection
from infrastructure.repositories.image_repository import SQLImageRepository
from application.services.image_service import ImageService
from domain.entities import ImageMetadata, User
from api.v1.auth import get_current_user

router = APIRouter(prefix="/images", tags=["Images"])


async def get_image_service(
    conn: asyncpg.Connection = Depends(get_db_connection),
) -> ImageService:
    repo = SQLImageRepository(conn)
    return ImageService(repo)


@router.post("/", response_model=ImageMetadata, status_code=status.HTTP_201_CREATED)
async def add_image(
    asset_id: UUID,
    url: str,
    name: str,
    alt_text: Optional[str] = None,
    is_main: bool = False,
    metadata_extra: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    service: ImageService = Depends(get_image_service),
):
    """
    Adds metadata for an already uploaded image. 
    In the future, this endpoint can be expanded to handle direct file uploads.
    """
    try:
        return await service.add_image_metadata(
            asset_id=asset_id,
            url=url,
            name=name,
            alt_text=alt_text,
            is_main=is_main,
            **(metadata_extra or {})
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/asset/{asset_id}", response_model=List[ImageMetadata])
async def get_asset_images(
    asset_id: UUID, 
    service: ImageService = Depends(get_image_service)
):
    return await service.get_asset_images(asset_id)


@router.post("/{image_id}/set-main")
async def set_main_image(
    image_id: UUID,
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ImageService = Depends(get_image_service),
):
    success = await service.set_main_image(asset_id, image_id)
    if not success:
        raise HTTPException(status_code=404, detail="Image or Asset not found")
    return {"message": "Main image updated successfully"}


@router.delete("/{image_id}")
async def delete_image(
    image_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ImageService = Depends(get_image_service),
):
    success = await service.delete_image(image_id)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image and metadata deleted successfully"}


@router.patch("/{image_id}", response_model=ImageMetadata)
async def update_image_metadata(
    image_id: UUID,
    metadata: dict,
    current_user: User = Depends(get_current_user),
    service: ImageService = Depends(get_image_service),
):
    updated = await service.update_metadata(image_id, metadata)
    if not updated:
        raise HTTPException(status_code=404, detail="Image not found")
    return updated
