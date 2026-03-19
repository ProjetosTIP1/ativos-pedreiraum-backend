from typing import List, Optional
from uuid import UUID, uuid4
import os
import aiofiles
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
        name: str,
        alt_text: Optional[str] = None,
        is_main: bool = False,
        position: Optional[str] = "OTHERS",
        **extra_metadata,
    ) -> ImageMetadata:
        """
        Validates, saves the file locally, and stores metadata in the database.
        """
        try:
            # 1. Validate extension
            allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
            _, ext = os.path.splitext(file.filename or "")
            ext = ext.lower()
            if ext not in allowed_extensions:
                raise ValidationServiceException(
                    f"Invalid file type. Allowed: {allowed_extensions}"
                )

            # Normalize position to match Enum
            norm_position = "OTHERS"
            if position:
                norm_position = position.upper().replace(" ", "_")
                # Basic check if it's a valid position, otherwise fallback to OTHERS
                from domain.enums import ImagePosition
                try:
                    ImagePosition(norm_position)
                except ValueError:
                    norm_position = "OTHERS"

            # 2. Generate secure random filename
            filename = f"{uuid4().hex}{ext}"
            file_path = os.path.join(settings.UPLOAD_DIR, filename)

            # 3. Save file locally using aiofiles for async I/O
            try:
                async with aiofiles.open(file_path, "wb") as out_file:
                    while content := await file.read(1024 * 1024):  # 1MB chunks
                        await out_file.write(content)
            except Exception as e:
                raise InfrastructureServiceException(
                    f"Failed to save file: {str(e)}"
                ) from e

            # 4. Determine URL and save metadata
            # The URL should be relative for the static file route mount
            url = f"/images/{filename}"

            # Get file size
            size = os.path.getsize(file_path)

            image = ImageMetadata(
                id=uuid4(),
                asset_id=asset_id,
                url=url,
                name=name,
                alt_text=alt_text,
                is_main=False,  # Always create as False initially to avoid DB constraint violation
                content_type=file.content_type,
                size=size,
                position=norm_position,
                **extra_metadata,
            )

            created_image: ImageMetadata | None = await self.image_repo.create(image)

            # If it's intended to be main, use the repo method which handles the transaction safely
            if is_main:
                await self.image_repo.set_main_image(asset_id, created_image.id)
                # Fetch updated image to return correct state
                created_image = await self.image_repo.get_by_id(created_image.id)
                if not created_image:
                    raise NotFoundServiceException("Image not found")

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
            if deleted and image.url.startswith("/uploads/"):
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

    async def update_metadata(
        self, image_id: UUID, metadata: dict
    ) -> Optional[ImageMetadata]:
        try:
            return await self.image_repo.update(image_id, metadata)
        except ServiceException:
            raise
        except ValueError as e:
            raise ValidationServiceException(str(e)) from e
        except Exception as e:
            raise InfrastructureServiceException(
                "Failed to update image metadata"
            ) from e
