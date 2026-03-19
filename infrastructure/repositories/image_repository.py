import asyncpg
from typing import List, Optional
from uuid import UUID
from domain.entities import ImageMetadata
from domain.interfaces import IImageRepository
from core.helpers.logger_helper import logger


class SQLImageRepository(IImageRepository):
    def __init__(self, connection: asyncpg.Connection):
        try:
            self.connection = connection
        except Exception as e:
            logger.error(f"Error initializing SQLImageRepository: {e}")
            raise

    async def get_by_id(self, image_id: UUID) -> Optional[ImageMetadata]:
        try:
            sql = """SELECT id,
            asset_id,
            url,
            is_main,
            position,
            created_at
            FROM image_metadata WHERE id = $1"""
            row = await self.connection.fetchrow(sql, image_id)
            if row:
                return ImageMetadata.model_validate(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error fetching image by ID {image_id}: {e}")
            raise

    async def list_by_asset(self, asset_id: UUID) -> List[ImageMetadata]:
        try:
            sql = """SELECT id,
            asset_id,
            url,
            is_main,
            position,
            created_at
            FROM image_metadata WHERE asset_id = $1 ORDER BY created_at ASC"""
            rows = await self.connection.fetch(sql, asset_id)
            return [ImageMetadata.model_validate(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error listing images for asset {asset_id}: {e}")
            raise

    async def create(self, image: ImageMetadata) -> ImageMetadata:
        try:
            image_dict = image.model_dump(exclude={"created_at"})

            # Convert Pydantic types to basic ones that asyncpg understands
            for key, value in image_dict.items():
                if hasattr(value, "value") and not isinstance(value, str):  # Enums
                    image_dict[key] = value.value

            columns = ", ".join(image_dict.keys())
            placeholders = ", ".join([f"${i + 1}" for i in range(len(image_dict))])
            values = list(image_dict.values())

            async with self.connection.transaction():
                sql = f"""INSERT INTO image_metadata ({columns}) VALUES ({placeholders}) RETURNING id,
                asset_id,
                url,
                is_main,
                position,
                created_at"""
                row = await self.connection.fetchrow(sql, *values)
                if not row:
                    raise Exception("Failed to create image metadata")
                created_image = ImageMetadata.model_validate(dict(row))

                # If this is the first image, make it the main one automatically
                count = await self.connection.fetchval(
                    "SELECT COUNT(*) FROM image_metadata WHERE asset_id = $1",
                    image.asset_id,
                )
                if count == 1:
                    await self.set_main_image(image.asset_id, created_image.id)
                    # Refresh to get is_main = True
                    created_image = await self.get_by_id(created_image.id)
                if not created_image:
                    raise Exception("Failed to refresh image metadata")
                return created_image
        except Exception as e:
            logger.error(f"Error creating image metadata: {e}")
            raise

    async def delete(self, image_id: UUID) -> bool:
        try:
            image = await self.get_by_id(image_id)
            if not image:
                return False

            async with self.connection.transaction():
                # If it was the main image, pick another one or set to empty
                if image.is_main:
                    await self.connection.execute(
                        "UPDATE assets SET main_image = '' WHERE id = $1",
                        image.asset_id,
                    )
                    # Try to find another image to be main
                    next_image = await self.connection.fetchrow(
                        "SELECT id FROM image_metadata WHERE asset_id = $1 AND id != $2 LIMIT 1",
                        image.asset_id,
                        image_id,
                    )
                    if next_image:
                        await self.set_main_image(image.asset_id, next_image["id"])

                sql = "DELETE FROM image_metadata WHERE id = $1"
                result = await self.connection.execute(sql, image_id)
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Error deleting image metadata {image_id}: {e}")
            raise

    async def set_main_image(self, asset_id: UUID, image_id: UUID) -> bool:
        try:
            # Start a transaction within the current connection
            async with self.connection.transaction():
                # Reset all images for this asset to not-main
                await self.connection.execute(
                    "UPDATE image_metadata SET is_main = FALSE WHERE asset_id = $1",
                    asset_id,
                )
                # Set the specific image as main
                result = await self.connection.execute(
                    "UPDATE image_metadata SET is_main = TRUE WHERE id = $1 AND asset_id = $2",
                    image_id,
                    asset_id,
                )

                # Also update the main_image field in the assets table for quick access
                image = await self.get_by_id(image_id)
                if image:
                    await self.connection.execute(
                        "UPDATE assets SET main_image = $1 WHERE id = $2",
                        str(image.url),
                        asset_id,
                    )

                return result == "UPDATE 1"
        except Exception as e:
            logger.error(
                f"Error setting main image {image_id} for asset {asset_id}: {e}"
            )
            raise
