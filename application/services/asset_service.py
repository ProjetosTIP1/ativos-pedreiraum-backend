import re
from typing import List, Optional
from uuid import UUID
from domain.entities import Asset
from domain.enums import AssetStatus
from domain.interfaces import IAssetRepository, ICategoryRepository
from core.helpers.exceptions_helper import (
    ServiceException,
    ValidationServiceException,
    InfrastructureServiceException,
)


class AssetService:
    def __init__(
        self, asset_repo: IAssetRepository, category_repo: ICategoryRepository
    ):
        try:
            self.asset_repo = asset_repo
            self.category_repo = category_repo
        except Exception as e:
            raise InfrastructureServiceException(
                "Failed to initialize asset service"
            ) from e

    async def get_all_assets(self, **filters) -> List[Asset]:
        try:
            return await self.asset_repo.list(**filters)
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to list assets") from e

    async def get_asset_by_slug(self, slug: str) -> Optional[Asset]:
        try:
            asset = await self.asset_repo.get_by_slug(slug)
            if asset:
                await self.asset_repo.increment_view_count(asset.id)
            return asset
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to fetch asset by slug") from e

    async def get_featured_assets(self) -> List[Asset]:
        try:
            return await self.asset_repo.get_featured()
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException(
                "Failed to fetch featured assets"
            ) from e

    async def create_asset(
        self, asset_data: dict, user_id: Optional[UUID] = None
    ) -> Asset:
        try:
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
        except ServiceException:
            raise
        except ValueError as e:
            raise ValidationServiceException(str(e)) from e
        except Exception as e:
            raise InfrastructureServiceException("Failed to create asset") from e

    async def update_asset(self, asset_id: UUID, asset_data: dict) -> Optional[Asset]:
        try:
            # Business Rule: No asset can be deleted or potentially modified if it has "RESERVED" status
            # (simplified check, usually depends on what's being modified)
            return await self.asset_repo.update(asset_id, asset_data)
        except ServiceException:
            raise
        except ValueError as e:
            raise ValidationServiceException(str(e)) from e
        except Exception as e:
            raise InfrastructureServiceException("Failed to update asset") from e

    async def delete_asset(self, asset_id: UUID) -> bool:
        try:
            asset = await self.asset_repo.get_by_id(asset_id)
            if not asset:
                return False

            # Business Rule: No asset can be deleted if it has "RESERVED" status
            if asset.status == "RESERVED":
                raise ValidationServiceException("Cannot delete a reserved asset.")

            return await self.asset_repo.delete(asset_id)
        except ServiceException:
            raise
        except ValueError as e:
            raise ValidationServiceException(str(e)) from e
        except Exception as e:
            raise InfrastructureServiceException("Failed to delete asset") from e

    def _generate_slug(self, text: str) -> str:
        try:
            text = text.lower()
            text = re.sub(r"[^\w\s-]", "", text)
            text = re.sub(r"[\s_-]+", "-", text)
            return text.strip("-")
        except Exception as e:
            raise ValidationServiceException("Failed to generate slug") from e
