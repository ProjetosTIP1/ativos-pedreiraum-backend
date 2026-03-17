import asyncpg
from typing import List, Optional
from uuid import UUID
from domain.entities import ImageMetadata
from domain.interfaces import IImageRepository
from core.helpers.logger_helper import logger

IMAGE_COLUMNS = "id, asset_id, url, name, alt_text, content_type, size, width, height, is_main, created_at"


class SQLImageRepository(IImageRepository):
    def __init__(self, connection: asyncpg.Connection):
        try:
            self.connection = connection
        except Exception as e:
            logger.error(f"Error initializing SQLImageRepository: {e}")
            raise

    async def get_by_id(self, image_id: UUID) -> Optional[ImageMetadata]:
        try:
            sql = f"SELECT {IMAGE_COLUMNS} FROM image_metadata WHERE id = $1"
            row = await self.connection.fetchrow(sql, image_id)
            if row:
                return ImageMetadata.model_validate(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error fetching image by ID {image_id}: {e}")
            raise

    async def list_by_asset(self, asset_id: UUID) -> List[ImageMetadata]:
        try:
            sql = f"SELECT {IMAGE_COLUMNS} FROM image_metadata WHERE asset_id = $1 ORDER BY created_at ASC"
            rows = await self.connection.fetch(sql, asset_id)
            return [ImageMetadata.model_validate(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error listing images for asset {asset_id}: {e}")
            raise

    async def create(self, image: ImageMetadata) -> ImageMetadata:
        try:
            image_dict = image.model_dump(exclude={"created_at"})

            # Convert Pydantic HttpUrl to string
            if "url" in image_dict:
                image_dict["url"] = str(image_dict["url"])

            columns = ", ".join(image_dict.keys())
            placeholders = ", ".join([f"${i + 1}" for i in range(len(image_dict))])
            values = list(image_dict.values())

            sql = f"INSERT INTO image_metadata ({columns}) VALUES ({placeholders}) RETURNING {IMAGE_COLUMNS}"
            row = await self.connection.fetchrow(sql, *values)
            return ImageMetadata.model_validate(dict(row))
        except Exception as e:
            logger.error(f"Error creating image metadata: {e}")
            raise

    async def update(self, image_id: UUID, image_data: dict) -> Optional[ImageMetadata]:
        try:
            if not image_data:
                return await self.get_by_id(image_id)

            set_clauses = [f"{k} = ${i + 1}" for i, k in enumerate(image_data.keys())]
            values = list(image_data.values())

            idx = len(values) + 1
            sql = f"UPDATE image_metadata SET {', '.join(set_clauses)} WHERE id = ${idx} RETURNING {IMAGE_COLUMNS}"
            values.append(image_id)

            row = await self.connection.fetchrow(sql, *values)
            if row:
                return ImageMetadata.model_validate(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error updating image metadata {image_id}: {e}")
            raise

    async def delete(self, image_id: UUID) -> bool:
        try:
            sql = "DELETE FROM image_metadata WHERE id = $1"
            result = await self.connection.execute(sql, image_id)
            return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Error deleting image metadata {image_id}: {e}")
            raise

    async def set_main_image(self, asset_id: UUID, image_id: UUID) -> bool:
        try:
            # 1. Start a transaction within the current connection
            async with self.connection.transaction():
                # 2. Reset all images for this asset to not-main
                await self.connection.execute(
                    "UPDATE image_metadata SET is_main = FALSE WHERE asset_id = $1",
                    asset_id,
                )
                # 3. Set the specific image as main
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
