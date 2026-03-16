from typing import List, Optional
from uuid import UUID, uuid4
import os
import aiofiles
from fastapi import UploadFile, HTTPException
from core.config import settings
from domain.entities import ImageMetadata
from domain.interfaces import IImageRepository


class ImageService:
    def __init__(self, image_repo: IImageRepository):
        self.image_repo = image_repo

    async def upload_and_save_metadata(
        self,
        asset_id: UUID,
        file: UploadFile,
        name: str,
        alt_text: Optional[str] = None,
        is_main: bool = False,
        **extra_metadata,
    ) -> ImageMetadata:
        """
        Validates, saves the file locally, and stores metadata in the database.
        """
        # 1. Validate extension
        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
        _, ext = os.path.splitext(file.filename or "")
        ext = ext.lower()
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {allowed_extensions}",
            )

        # 2. Generate secure random filename
        filename = f"{uuid4().hex}{ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        # 3. Save file locally using aiofiles for async I/O
        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                while content := await file.read(1024 * 1024):  # 1MB chunks
                    await out_file.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to save file: {str(e)}"
            )

        # 4. Determine URL and save metadata
        # The URL should be relative for the static file route mount
        url = f"/uploads/{filename}"

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
            **extra_metadata,
        )

        created_image: ImageMetadata | None = await self.image_repo.create(image)

        # If it's intended to be main, use the repo method which handles the transaction safely
        if is_main:
            await self.image_repo.set_main_image(asset_id, created_image.id)
            # Fetch updated image to return correct state
            created_image = await self.image_repo.get_by_id(created_image.id)
            if not created_image:
                raise HTTPException(status_code=404, detail="Image not found")

        return created_image

    async def get_asset_images(self, asset_id: UUID) -> List[ImageMetadata]:
        return await self.image_repo.list_by_asset(asset_id)

    async def set_main_image(self, asset_id: UUID, image_id: UUID) -> bool:
        return await self.image_repo.set_main_image(asset_id, image_id)

    async def delete_image(self, image_id: UUID) -> bool:
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
                except Exception as e:
                    print(f"Warning: Failed to delete physical file {file_path}: {e}")

        return deleted

    async def update_metadata(
        self, image_id: UUID, metadata: dict
    ) -> Optional[ImageMetadata]:
        return await self.image_repo.update(image_id, metadata)
