import os
import aiofiles
import filetype
from typing import List, Optional
from uuid import UUID, uuid4
from fastapi import UploadFile, HTTPException
from core.config import settings
from domain.entities import ImageMetadata
from domain.interfaces import IImageRepository
from core.helpers.exceptions_helper import (
    ServiceException,
    ValidationServiceException,
    NotFoundServiceException,
    InfrastructureServiceException,
)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/avif"}
# Maps mime types to safe extensions to avoid trusting user-provided extensions
MIME_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/avif": ".avif",
}


class ImageService:
    def __init__(self, image_repo: IImageRepository):
        try:
            self.image_repo = image_repo
        except Exception as e:
            raise InfrastructureServiceException(
                "Failed to initialize image service"
            ) from e

    async def upload_and_save_metadata(
        self,
        asset_id: UUID,
        file: UploadFile,
        is_main: bool = False,
        position: Optional[str] = "OUTROS",
    ) -> ImageMetadata:
        """
        Validates, saves the file locally, and stores metadata in the database.
        """
        try:
            filename = await self._validate_image_content(file)

            # Normalize position to match Enum
            norm_position = "OUTROS"
            if position:
                norm_position = position.upper().replace(" ", "_")
                # Basic check if it's a valid position, otherwise fallback to OTHERS
                from domain.enums import ImagePosition

                try:
                    ImagePosition(norm_position)
                except ValueError:
                    norm_position = "OUTROS"

            # 2. Generate secure random filename
            file_path = os.path.join(settings.UPLOAD_DIR, filename)

            # 3. Determine URL and save metadata
            # The URL should be relative for the static file route mount
            url = filename

            image = ImageMetadata(
                id=uuid4(),
                asset_id=asset_id,
                url=url,
                is_main=is_main,
                position=ImagePosition(norm_position),
            )

            # Check if asset already has an image with this position
            images_metadata = await self.image_repo.list_by_asset(asset_id)
            for image_metadata in images_metadata:
                if image_metadata.position == norm_position:
                    await self.image_repo.delete(image_metadata.id)

            created_image: ImageMetadata | None = await self.image_repo.create(image)

            if not created_image:
                raise NotFoundServiceException("Image not found")

            # If it's intended to be main, use the repo method which handles the transaction safely
            if is_main:
                await self.image_repo.set_main_image(asset_id, created_image.id)
                # Fetch updated image to return correct state
                created_image = await self.image_repo.get_by_id(created_image.id)
                if not created_image:
                    raise NotFoundServiceException("Image not found")

            # 4. Save file locally using aiofiles for async I/O
            # This is the last step to prevent orphaned files
            try:
                # Ensure the directory exists
                os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

                async with aiofiles.open(file_path, "wb") as out_file:
                    while content := await file.read(1024 * 1024):  # 1MB chunks
                        await out_file.write(content)
            except Exception as e:
                raise InfrastructureServiceException(
                    f"Failed to save file: {str(e)}"
                ) from e

            return created_image
        except ServiceException:
            raise
        except HTTPException as e:
            raise ValidationServiceException(str(e.detail)) from e
        except ValueError as e:
            raise ValidationServiceException(str(e)) from e
        except Exception as e:
            raise InfrastructureServiceException(
                "Failed to upload image metadata"
            ) from e

    async def get_asset_images(self, asset_id: UUID) -> List[ImageMetadata]:
        try:
            return await self.image_repo.list_by_asset(asset_id)
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to list asset images") from e

    async def set_main_image(self, asset_id: UUID, image_id: UUID) -> bool:
        try:
            return await self.image_repo.set_main_image(asset_id, image_id)
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to set main image") from e

    async def delete_image(self, image_id: UUID) -> bool:
        try:
            # First get the image to find its URL
            image = await self.image_repo.get_by_id(image_id)
            if not image:
                return False

            # Attempt to delete from DB
            deleted = await self.image_repo.delete(image_id)

            # If deleted from DB, remove the physical file
            if deleted and image.url.startswith("/images/"):
                filename = image.url.split("/")[-1]
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        # Keep DB deletion success even if physical cleanup fails.
                        pass

            return deleted
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to delete image") from e

    async def _validate_image_content(self, file: UploadFile) -> str:
        """
        Refactored System Design:
        1. Size Validation (Shield)
        2. Content Validation (Magic Numbers/Pillow)
        3. Metadata Sanitization (Security)
        4. Atomic Persistence (Reliability)
        """

        # --- 1. PRE-FLIGHT VALIDATION (The Guard) ---

        # A. Check Size (Don't read the whole file into RAM yet)
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > MAX_FILE_SIZE:
            raise ValidationServiceException(
                f"File too large. Max allowed: {MAX_FILE_SIZE / 1e6}MB"
            )

        # B. Validate Content (Magic Numbers)
        # Read the first 2048 bytes to detect the "real" mime type
        header = await file.read(2048)
        await file.seek(0)

        # Use filetype to guess the mime type
        kind = filetype.guess(header)

        if kind is None:
            raise ValidationServiceException("Cannot identify file type.")

        # Validate against our allowed list
        if kind.mime not in ALLOWED_MIME_TYPES:
            raise ValidationServiceException(f"Unsupported file type: {kind.mime}")

        # Use the extension from the verified 'kind', NOT the user's filename
        safe_ext = f".{kind.extension}"
        unique_name: str = f"{uuid4().hex}{safe_ext}"
        return unique_name
