import json
from typing import List, Optional
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from domain.entities import Asset, AssetCategory
from domain.interfaces import IAssetRepository


class SQLAssetRepository(IAssetRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, asset_id: UUID) -> Optional[Asset]:
        query = text("SELECT * FROM assets WHERE id = :id")
        result = await self.session.execute(query, {"id": asset_id})
        row = result.mappings().first()
        if row:
            return Asset.model_validate(dict(row))
        return None

    async def get_by_slug(self, slug: str) -> Optional[Asset]:
        query = text("SELECT * FROM assets WHERE slug = :slug")
        result = await self.session.execute(query, {"slug": slug})
        row = result.mappings().first()
        if row:
            return Asset.model_validate(dict(row))
        return None

    async def list(
        self,
        category: Optional[AssetCategory] = None,
        brand: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        query: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Asset]:
        sql = "SELECT * FROM assets WHERE 1=1"
        params = {"limit": limit, "offset": offset}

        if category:
            sql += " AND category = :category"
            params["category"] = category.value
        if brand:
            sql += " AND brand ILIKE :brand"
            params["brand"] = f"%{brand}%"
        if min_year:
            sql += " AND year >= :min_year"
            params["min_year"] = min_year
        if max_year:
            sql += " AND year <= :max_year"
            params["max_year"] = max_year
        if query:
            sql += " AND search_vector @@ to_tsquery('portuguese', :query)"
            params["query"] = " & ".join(query.split())

        sql += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"

        result = await self.session.execute(text(sql), params)
        return [Asset.model_validate(dict(row)) for row in result.mappings().all()]

    async def get_featured(self) -> List[Asset]:
        query = text(
            "SELECT * FROM assets WHERE is_featured = TRUE ORDER BY created_at DESC LIMIT 5"
        )
        result = await self.session.execute(query)
        return [Asset.model_validate(dict(row)) for row in result.mappings().all()]

    async def create(self, asset: Asset) -> Asset:
        asset_dict = json.loads(asset.model_dump_json(exclude={"created_at"}))

        columns = ", ".join(asset_dict.keys())
        placeholders = ", ".join([f":{k}" for k in asset_dict.keys()])

        sql = f"INSERT INTO assets ({columns}) VALUES ({placeholders}) RETURNING *"
        result = await self.session.execute(text(sql), asset_dict)
        row = result.mappings().first()
        await self.session.commit()
        if not row:
            raise Exception("Failed to create asset")
        return Asset.model_validate(dict(row))

    async def update(self, asset_id: UUID, asset_data: dict) -> Optional[Asset]:
        if not asset_data:
            return await self.get_by_id(asset_id)

        set_clause = ", ".join([f"{k} = :{k}" for k in asset_data.keys()])
        params = {**asset_data, "id": asset_id}

        sql = f"UPDATE assets SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = :id RETURNING *"
        result = await self.session.execute(text(sql), params)
        row = result.mappings().first()
        await self.session.commit()
        if row:
            return Asset.model_validate(dict(row))
        return None

    async def delete(self, asset_id: UUID) -> bool:
        query = text("DELETE FROM assets WHERE id = :id")
        result = await self.session.execute(query, {"id": asset_id})
        await self.session.commit()
        return getattr(result, "rowcount", 0) > 0  # Use getattr for safety

    async def increment_view_count(self, asset_id: UUID) -> None:
        query = text("UPDATE assets SET view_count = view_count + 1 WHERE id = :id")
        await self.session.execute(query, {"id": asset_id})
        await self.session.commit()
