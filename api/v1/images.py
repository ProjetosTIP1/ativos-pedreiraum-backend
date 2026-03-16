import asyncpg
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
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
    asset_id: UUID = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...),
    alt_text: Optional[str] = Form(None),
    is_main: bool = Form(False),
    current_user: User = Depends(get_current_user),
    service: ImageService = Depends(get_image_service),  # noqa: B008
):
    """
    Uploads an image file to local storage and saves metadata.
    """
    try:
        return await service.upload_and_save_metadata(
            asset_id=asset_id,
            file=file,
            name=name,
            alt_text=alt_text,
            is_main=is_main
        )
    except HTTPException:
        raise
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
