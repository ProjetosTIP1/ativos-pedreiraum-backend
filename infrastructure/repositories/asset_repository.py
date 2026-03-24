import asyncpg
from typing import List, Optional
from uuid import UUID

from domain.entities import Asset, CreateAssetRequest, UpdateAssetRequest
from domain.enums import AssetCategory, AssetStatus
from domain.interfaces import IAssetRepository
from core.helpers.logger_helper import logger


class SQLAssetRepository(IAssetRepository):
    def __init__(self, connection: asyncpg.Connection):
        try:
            self.connection = connection
        except Exception as e:
            logger.error(f"Error initializing SQLAssetRepository: {e}")
            raise

    async def get_by_id(self, asset_id: UUID) -> Optional[Asset]:
        try:
            query = """SELECT id,
            name,
            category,
            subcategory,
            brand,
            model,
            year,
            serial_number,
            location,
            condition,
            status,
            price,
            description,
            rep_contact,
            highlighted,
            view_count,
            created_by_user_id,
            specifications,
            created_at,
            updated_at
            FROM assets WHERE id = $1 AND is_active = TRUE AND deleted_at IS NULL"""
            row = await self.connection.fetchrow(query, asset_id)
            if row:
                return Asset.model_validate(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error fetching asset by ID: {e}")
            raise

    async def get_by_slug(self, slug: str) -> Optional[Asset]:
        try:
            query = """SELECT id,
            name,
            category,
            subcategory,
            brand,
            model,
            year,
            serial_number,
            location,
            condition,
            status,
            price,
            description,
            rep_contact,
            highlighted,
            view_count,
            created_by_user_id,
            specifications,
            created_at,
            updated_at
            FROM assets WHERE slug = $1 AND is_active = TRUE AND deleted_at IS NULL"""
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
        status: Optional[AssetStatus] = None,
        user_id: Optional[UUID] = None,
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
            if status:
                filters.append(f"status = ${idx}")
                values.append(status.value)
                idx += 1
            if user_id:
                filters.append(f"created_by_user_id = ${idx}")
                values.append(user_id)
                idx += 1

            # Always include base conditions
            filters.append("is_active = TRUE")
            filters.append("deleted_at IS NULL")

            where_clause = "WHERE " + " AND ".join(filters)
            sql = f"""SELECT id,
                      name,
                      category,
                      subcategory,
                      brand,
                      model,
                      year,
                      serial_number,
                      location,
                      condition,
                      status,
                      price,
                      description,
                      rep_contact,
                      highlighted,
                      view_count,
                      created_by_user_id,
                      specifications,
                      created_at,
                      updated_at
                      FROM assets {where_clause} ORDER BY created_at DESC LIMIT ${idx} OFFSET ${idx + 1}"""
            values.extend([limit, offset])

            rows = await self.connection.fetch(sql, *values)
            return [Asset.model_validate(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error listing assets: {e}")
            raise e

    async def get_featured(self) -> List[Asset]:
        try:
            query = """SELECT id,
                      name,
                      category,
                      subcategory,
                      brand,
                      model,
                      year,
                      serial_number,
                      location,
                      condition,
                      status,
                      price,
                      description,
                      rep_contact,
                      highlighted,
                      view_count,
                      created_by_user_id,
                      specifications,
                      created_at,
                      updated_at
                       FROM assets WHERE highlighted = TRUE AND status = 'DISPONÍVEL' AND is_active = TRUE AND deleted_at IS NULL ORDER BY created_at DESC LIMIT 5"""
            rows = await self.connection.fetch(query)
            return [Asset.model_validate(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching featured assets: {e}")
            raise

    async def create(self, asset: CreateAssetRequest) -> Asset:
        try:
            asset_dict = asset.model_dump(exclude={"created_at"}, exclude_none=True)

            columns = ", ".join(asset_dict.keys())
            # Use $1, $2, etc. placeholders
            placeholders = ", ".join([f"${i + 1}" for i in range(len(asset_dict))])
            values = list(asset_dict.values())

            sql = f"""INSERT INTO assets ({columns}) VALUES ({placeholders}) RETURNING id,
            name,
            category,
            subcategory,
            brand,
            model,
            year,
            serial_number,
            location,
            condition,
            status,
            price,
            description,
            rep_contact,
            highlighted,
            view_count,
            created_by_user_id,
            specifications,
            created_at,
            updated_at"""
            row = await self.connection.fetchrow(sql, *values)
            if not row:
                raise Exception("Failed to create asset")
            return Asset.model_validate(dict(row))
        except Exception as e:
            logger.error(f"Error creating asset: {e}")
            raise

    async def update(
        self, asset_id: UUID, asset_data: UpdateAssetRequest
    ) -> Optional[Asset]:
        try:
            if not asset_data:
                return await self.get_by_id(asset_id)

            asset_data_dict = asset_data.model_dump(exclude_unset=True)
            asset_data_dict.pop("id", None)
            asset_data_dict.pop("created_at", None)

            set_clauses = []
            values = []
            for i, (k, v) in enumerate(asset_data_dict.items()):
                set_clauses.append(f"{k} = ${i + 1}")
                values.append(v)

            idx = len(values) + 1
            sql = f"""UPDATE assets SET {", ".join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ${idx} RETURNING id,
            name,
            category,
            subcategory,
            brand,
            model,
            year,
            serial_number,
            location,
            condition,
            status,
            price,
            description,
            rep_contact,
            highlighted,
            view_count,
            created_by_user_id,
            specifications,
            created_at,
            updated_at"""
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
            query = "UPDATE assets SET deleted_at = CURRENT_TIMESTAMP, is_active = FALSE WHERE id = $1"
            result = await self.connection.execute(query, asset_id)
            # result is a string like 'UPDATE 1'
            return result == "UPDATE 1"
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
