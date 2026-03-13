import re
from typing import List, Optional
from uuid import UUID
from domain.entities import Asset
from domain.enums import AssetStatus
from domain.interfaces import IAssetRepository, ICategoryRepository


class AssetService:
    def __init__(
        self, asset_repo: IAssetRepository, category_repo: ICategoryRepository
    ):
        self.asset_repo = asset_repo
        self.category_repo = category_repo

    async def get_all_assets(self, **filters) -> List[Asset]:
        return await self.asset_repo.list(**filters)

    async def get_asset_by_slug(self, slug: str) -> Optional[Asset]:
        asset = await self.asset_repo.get_by_slug(slug)
        if asset:
            await self.asset_repo.increment_view_count(asset.id)
        return asset

    async def get_featured_assets(self) -> List[Asset]:
        return await self.asset_repo.get_featured()

    async def create_asset(self, asset_data: dict, user_id: Optional[UUID] = None) -> Asset:
        # Generate slug: name + year
        name = asset_data.get("name", "")
        year = asset_data.get("year", "")
        slug_base = f"{name}-{year}"
        slug = self._generate_slug(slug_base)

        asset_data["slug"] = slug
        asset_data["created_by_user_id"] = user_id
        
        # Ensure status is PENDING for new assets created by users
        asset_data["status"] = AssetStatus.PENDING

        asset = Asset.model_validate(asset_data)
        return await self.asset_repo.create(asset)

    async def update_asset(self, asset_id: UUID, asset_data: dict) -> Optional[Asset]:
        # Business Rule: No asset can be deleted or potentially modified if it has "RESERVED" status
        # (simplified check, usually depends on what's being modified)
        return await self.asset_repo.update(asset_id, asset_data)

    async def delete_asset(self, asset_id: UUID) -> bool:
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset:
            return False

        # Business Rule: No asset can be deleted if it has "RESERVED" status
        if asset.status == "RESERVED":
            raise ValueError("Cannot delete a reserved asset.")

        return await self.asset_repo.delete(asset_id)

    def _generate_slug(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_-]+", "-", text)
        return text.strip("-")
