from fastapi.responses import FileResponse
from datetime import datetime
import mimetypes
import uuid
from pathlib import Path
import asyncpg
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
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
    file: UploadFile, current_user: User = Depends(get_current_user)
) -> ImageMetadata:
    """
    Upload an image and return its metadata.

    This endpoint follows Clean Architecture principles:
    - Single Responsibility: Handles only image upload logic
    - Input Validation: Validates file type, size, and security
    - Error Handling: Comprehensive error management with meaningful messages

    Accepts multipart/form-data with an image file.
    Supported formats: JPEG, PNG, GIF, WebP
    Maximum file size: 10MB
    """

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    # Step 1: Validate file exists and has content
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Step 2: Validate file type (Security - prevent malicious uploads)
    allowed_content_types = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
    }

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(allowed_content_types)}",
        )

    # Step 3: Validate file size (10MB limit)
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {max_size / (1024 * 1024):.1f}MB",
        )

    # Step 4: Generate secure filename (prevent directory traversal)
    file_extension = Path(file.filename).suffix.lower()
    if not file_extension:
        # Determine extension from content type
        extension_map = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
        }
        file_extension = extension_map.get(file.content_type, ".jpg")

    # Generate unique filename to prevent conflicts
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"

    # Step 5: Ensure images directory exists
    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)

    # Step 6: Save file securely
    file_path = images_dir / unique_filename

    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
        print(f"Image successfully saved to: {file_path}", "DEBUG")
    except IOError as e:
        print(f"Error saving image: {e}", "ERROR")
        raise HTTPException(status_code=500, detail="Failed to save image")

    # Step 7: Determine actual MIME type from file content
    actual_mime_type = mimetypes.guess_type(str(file_path))[0] or file.content_type

    # Step 8: Create and return metadata
    image_metadata = ImageMetadata(
        filename=unique_filename,
        url=f"/images/{unique_filename}",
        alt_text=f"Image uploaded as {unique_filename}",
        size=len(file_content),
        mime_type=actual_mime_type,
        upload_date=datetime.now().isoformat(),
    )
    return image_metadata


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
    images_dir = Path("images")
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
        print(f"Image not found: {filename}", "WARNING")
        raise HTTPException(status_code=404, detail="Image not found")

    # Step 5: Validate it's actually a file (not a directory)
    if not image_path.is_file():
        raise HTTPException(status_code=400, detail="Invalid file")

    # Step 6: Return file with appropriate headers
    print(f"Serving image: {filename}", "DEBUG")
    return FileResponse(
        path=str(image_path),
        media_type=mimetypes.guess_type(str(image_path))[0]
        or "application/octet-stream",
        filename=filename,
    )
