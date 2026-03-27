from fastapi.openapi.models import Response
from core.config import settings
from fastapi.responses import FileResponse
import mimetypes
from pathlib import Path
import asyncpg
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from core.database import get_db_connection
from infrastructure.repositories.image_repository import SQLImageRepository
from application.services.image_service import ImageService
from domain.entities import ImageMetadata, User
from api.v1.auth import get_current_user
from core.helpers.exceptions_helper import ServiceException, to_http_exception

router = APIRouter(prefix="/images", tags=["Images"])


async def get_image_service(
    conn: asyncpg.Connection = Depends(get_db_connection),
) -> ImageService:
    repo = SQLImageRepository(conn)
    return ImageService(repo)


@router.get("/asset/{asset_id}", response_model=List[ImageMetadata])
async def get_asset_images(
    asset_id: UUID, service: ImageService = Depends(get_image_service)
):
    try:
        return await service.get_asset_images(asset_id)
    except HTTPException:
        raise
    except ServiceException as e:
        raise to_http_exception(e)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=ImageMetadata)
async def upload_image(
    asset_id: UUID = Form(...),
    position: str = Form("OTHERS"),
    is_main: bool = Form(False),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: ImageService = Depends(get_image_service),
) -> ImageMetadata:
    """
    Upload an image associated with an asset.
    """

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    try:
        # Use the service for the entire flow: validation, storage, and metadata
        return await service.upload_and_save_metadata(
            asset_id=asset_id,
            file=file,
            is_main=is_main,
            position=position,
        )
    except ServiceException as e:
        raise to_http_exception(e)
    except Exception as e:
        print(f"Error in upload_image: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image")


@router.patch("/set_main/{image_id}", response_model=Response)
async def set_main_image(
    asset_id: UUID,
    image_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ImageService = Depends(get_image_service),
) -> Response:
    """
    Set an image as the main image for an asset.
    """

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    try:
        if await service.set_main_image(asset_id, image_id):
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to set main image",
            )
    except ServiceException as e:
        raise to_http_exception(e)
    except Exception as e:
        print(f"Error in set_main_image: {e}")
        raise HTTPException(status_code=500, detail="Failed to set main image")


@router.get("/{filename}", response_class=FileResponse)
async def get_image(filename: str) -> FileResponse:
    """
    Retrieve an image by filename using FileResponse.

    This endpoint follows Clean Architecture principles:
    - Single Responsibility: Serves image files only
    - Security First: Prevents directory traversal attacks
    - Error Handling: Comprehensive validation and meaningful errors

    This endpoint serves image files directly from the local filesystem.
    """
    print(f"Requesting image: {filename}", "DEBUG")

    # Step 1: Validate filename (Security - prevent directory traversal)
    if not filename or ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Step 2: Construct secure file path
    images_dir = Path(settings.UPLOAD_DIR)
    image_path = images_dir / filename

    # Step 3: Additional security check - ensure resolved path is within images directory
    try:
        resolved_path = image_path.resolve()
        images_dir_resolved = images_dir.resolve()

        if not str(resolved_path).startswith(str(images_dir_resolved)):
            raise HTTPException(status_code=403, detail="Access forbidden")
    except (OSError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid file path")

    # Step 4: Check if file exists
    if not image_path.exists():
        print(f"Image not found: {filename} - {image_path}", "WARNING")
        raise HTTPException(status_code=404, detail="Image not found")

    # Step 5: Validate it's actually a file (not a directory)
    if not image_path.is_file():
        raise HTTPException(status_code=400, detail="Invalid file")

    # Step 6: Return file with appropriate headers
    print(f"Serving image: {filename} - {image_path}", "DEBUG")
    return FileResponse(
        path=str(image_path),
        media_type=mimetypes.guess_type(str(image_path))[0]
        or "application/octet-stream",
        filename=filename,
    )
