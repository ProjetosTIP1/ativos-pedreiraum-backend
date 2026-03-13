from typing import List, Optional
from uuid import UUID, uuid4
from domain.entities import ImageMetadata
from domain.interfaces import IImageRepository

class ImageService:
    def __init__(self, image_repo: IImageRepository):
        self.image_repo = image_repo

    async def add_image_metadata(
        self, 
        asset_id: UUID, 
        url: str, 
        name: str, 
        alt_text: Optional[str] = None,
        is_main: bool = False,
        **extra_metadata
    ) -> ImageMetadata:
        """
        Saves metadata for an image. 
        If is_main is True, it will update other images for the asset.
        """
        image = ImageMetadata(
            id=uuid4(),
            asset_id=asset_id,
            url=str(url),
            name=name,
            alt_text=alt_text,
            is_main=is_main,
            **extra_metadata
        )
        
        created_image = await self.image_repo.create(image)
        
        if is_main:
            await self.image_repo.set_main_image(asset_id, created_image.id)
            
        return created_image

    async def get_asset_images(self, asset_id: UUID) -> List[ImageMetadata]:
        return await self.image_repo.list_by_asset(asset_id)

    async def set_main_image(self, asset_id: UUID, image_id: UUID) -> bool:
        return await self.image_repo.set_main_image(asset_id, image_id)

    async def delete_image(self, image_id: UUID) -> bool:
        # Note: In a real app, this would also delete the file from storage (Cloudinary/S3)
        return await self.image_repo.delete(image_id)

    async def update_metadata(self, image_id: UUID, metadata: dict) -> Optional[ImageMetadata]:
        return await self.image_repo.update(image_id, metadata)
