import asyncpg
from typing import List, Optional
from uuid import UUID

from domain.entities import Asset
from domain.enums import AssetCategory, AssetStatus
from domain.interfaces import IAssetRepository
from core.helpers.logger_helper import logger

ASSET_COLUMNS = """
    id, slug, name, category, subcategory, brand, model, year, 
    serial_number, location, condition, status, price, description, 
    main_image, gallery, is_featured, view_count, branch_id, 
    created_by_user_id, specifications, created_at
"""


class SQLAssetRepository(IAssetRepository):
    def __init__(self, connection: asyncpg.Connection):
        try:
            self.connection = connection
        except Exception as e:
            logger.error(f"Error initializing SQLAssetRepository: {e}")
            raise

    async def get_by_id(self, asset_id: UUID) -> Optional[Asset]:
        try:
            query = f"SELECT {ASSET_COLUMNS} FROM assets WHERE id = $1"
            row = await self.connection.fetchrow(query, asset_id)
            if row:
                return Asset.model_validate(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error fetching asset by ID: {e}")
            raise

    async def get_by_slug(self, slug: str) -> Optional[Asset]:
        try:
            query = f"SELECT {ASSET_COLUMNS} FROM assets WHERE slug = $1"
            row = await self.connection.fetchrow(query, slug)
            if row:
                return Asset.model_validate(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error fetching asset by slug: {e}")
            raise

    async def list(
        self,
        category: Optional[AssetCategory] = None,
        brand: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        branch_id: Optional[int] = None,
        status: Optional[AssetStatus] = None,
        query: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Asset]:
        try:
            filters = []
            values = []
            idx = 1

            if category:
                filters.append(f"category = ${idx}")
                values.append(category.value)
                idx += 1
            if brand:
                filters.append(f"brand ILIKE ${idx}")
                values.append(f"%{brand}%")
                idx += 1
            if min_year:
                filters.append(f"year >= ${idx}")
                values.append(min_year)
                idx += 1
            if max_year:
                filters.append(f"year <= ${idx}")
                values.append(max_year)
                idx += 1
            if branch_id:
                filters.append(f"branch_id = ${idx}")
                values.append(branch_id)
                idx += 1
            if status:
                filters.append(f"status = ${idx}")
                values.append(status.value)
                idx += 1
            if query:
                filters.append(
                    f"(name ILIKE ${idx} OR description ILIKE ${idx} OR brand ILIKE ${idx})"
                )
                values.append(f"%{query}%")
                idx += 1

            where_clause = "WHERE " + " AND ".join(filters) if filters else ""
            sql = f"SELECT {ASSET_COLUMNS} FROM assets {where_clause} ORDER BY created_at DESC LIMIT ${idx} OFFSET ${idx + 1}"
            values.extend([limit, offset])

            rows = await self.connection.fetch(sql, *values)
            return [Asset.model_validate(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error listing assets: {e}")
            raise e

    async def get_featured(self) -> List[Asset]:
        try:
            query = f"SELECT {ASSET_COLUMNS} FROM assets WHERE is_featured = TRUE AND status = 'AVAILABLE' ORDER BY created_at DESC LIMIT 5"
            rows = await self.connection.fetch(query)
            return [Asset.model_validate(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching featured assets: {e}")
            raise

    async def create(self, asset: Asset) -> Asset:
        try:
            asset_dict = asset.model_dump(exclude={"created_at"})

            # Convert Pydantic types to basic ones that asyncpg understands
            for key, value in asset_dict.items():
                if key == "specifications" and isinstance(value, dict):
                    import json

                    asset_dict[key] = json.dumps(value)
                elif key == "gallery" and isinstance(value, list):
                    # Ensure all elements are strings for TEXT[]
                    asset_dict[key] = [str(v) for v in value]
                elif hasattr(value, "value") and not isinstance(value, str):  # Enums
                    asset_dict[key] = value.value
                elif hasattr(value, "__str__") and "HttpUrl" in str(type(value)):
                    asset_dict[key] = str(value)

            columns = ", ".join(asset_dict.keys())
            # Use $1, $2, etc. placeholders
            placeholders = ", ".join([f"${i + 1}" for i in range(len(asset_dict))])
            values = list(asset_dict.values())

            sql = f"INSERT INTO assets ({columns}) VALUES ({placeholders}) RETURNING {ASSET_COLUMNS}"
            row = await self.connection.fetchrow(sql, *values)
            if not row:
                raise Exception("Failed to create asset")
            return Asset.model_validate(dict(row))
        except Exception as e:
            logger.error(f"Error creating asset: {e}")
            raise

    async def update(self, asset_id: UUID, asset_data: dict) -> Optional[Asset]:
        try:
            if not asset_data:
                return await self.get_by_id(asset_id)

            asset_data.pop("id", None)
            asset_data.pop("created_at", None)

            set_clauses = []
            values = []
            for i, (k, v) in enumerate(asset_data.items()):
                set_clauses.append(f"{k} = ${i + 1}")
                values.append(v)

            idx = len(values) + 1
            sql = f"UPDATE assets SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ${idx} RETURNING {ASSET_COLUMNS}"
            values.append(asset_id)

            row = await self.connection.fetchrow(sql, *values)
            if row:
                return Asset.model_validate(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error updating asset {asset_id}: {e}")
            raise

    async def delete(self, asset_id: UUID) -> bool:
        try:
            query = "DELETE FROM assets WHERE id = $1"
            result = await self.connection.execute(query, asset_id)
            # result is a string like 'DELETE 1'
            return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Error deleting asset {asset_id}: {e}")
            raise

    async def increment_view_count(self, asset_id: UUID) -> None:
        try:
            query = "UPDATE assets SET view_count = view_count + 1 WHERE id = $1"
            await self.connection.execute(query, asset_id)
        except Exception as e:
            logger.error(f"Error incrementing view count for asset {asset_id}: {e}")
            raise
