from typing import List, Optional
from uuid import UUID
import asyncpg
from domain.entities import Asset
from domain.enums import AssetCategory, AssetStatus
from domain.interfaces import IAssetRepository

ASSET_COLUMNS = """
    id, slug, name, category, subcategory, brand, model, year, 
    serial_number, location, condition, status, price, description, 
    main_image, gallery, is_featured, view_count, branch_id, 
    created_by_user_id, specifications, created_at
"""


class SQLAssetRepository(IAssetRepository):
    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection

    async def get_by_id(self, asset_id: UUID) -> Optional[Asset]:
        query = f"SELECT {ASSET_COLUMNS} FROM assets WHERE id = $1"
        row = await self.connection.fetchrow(query, asset_id)
        if row:
            return Asset.model_validate(dict(row))
        return None

    async def get_by_slug(self, slug: str) -> Optional[Asset]:
        query = f"SELECT {ASSET_COLUMNS} FROM assets WHERE slug = $1"
        row = await self.connection.fetchrow(query, slug)
        if row:
            return Asset.model_validate(dict(row))
        return None

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
        sql = f"SELECT {ASSET_COLUMNS} FROM assets WHERE 1=1"
        params = []
        param_idx = 1

        if category:
            sql += f" AND category = ${param_idx}"
            params.append(category.value)
            param_idx += 1
        if brand:
            sql += f" AND brand ILIKE ${param_idx}"
            params.append(f"%{brand}%")
            param_idx += 1
        if min_year:
            sql += f" AND year >= ${param_idx}"
            params.append(min_year)
            param_idx += 1
        if max_year:
            sql += f" AND year <= ${param_idx}"
            params.append(max_year)
            param_idx += 1
        if branch_id:
            sql += f" AND branch_id = ${param_idx}"
            params.append(branch_id)
            param_idx += 1
        if status:
            sql += f" AND status = ${param_idx}"
            params.append(status.value)
            param_idx += 1
        if query:
            sql += f" AND search_vector @@ to_tsquery('portuguese', ${param_idx})"
            params.append(" & ".join(query.split()))
            param_idx += 1

        sql += f" ORDER BY created_at DESC LIMIT ${param_idx} OFFSET ${param_idx + 1}"
        params.extend([limit, offset])

        rows = await self.connection.fetch(sql, *params)
        return [Asset.model_validate(dict(row)) for row in rows]

    async def get_featured(self) -> List[Asset]:
        query = f"SELECT {ASSET_COLUMNS} FROM assets WHERE is_featured = TRUE AND status = 'AVAILABLE' ORDER BY created_at DESC LIMIT 5"
        rows = await self.connection.fetch(query)
        return [Asset.model_validate(dict(row)) for row in rows]

    async def create(self, asset: Asset) -> Asset:
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

    async def update(self, asset_id: UUID, asset_data: dict) -> Optional[Asset]:
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

    async def delete(self, asset_id: UUID) -> bool:
        query = "DELETE FROM assets WHERE id = $1"
        result = await self.connection.execute(query, asset_id)
        # result is a string like 'DELETE 1'
        return result == "DELETE 1"

    async def increment_view_count(self, asset_id: UUID) -> None:
        query = "UPDATE assets SET view_count = view_count + 1 WHERE id = $1"
        await self.connection.execute(query, asset_id)
