from uuid import UUID
from typing import Optional
from domain.entities import Asset
from domain.enums import AssetStatus
from domain.interfaces import IAssetRepository


class AssetApprovalService:
    def __init__(self, asset_repo: IAssetRepository):
        self.asset_repo = asset_repo

    async def approve_asset(
        self, asset_id: UUID, final_data: Optional[dict] = None
    ) -> Optional[Asset]:
        """
        Approves an asset, optionally updating its details (price, etc.)
        and setting status to AVAILABLE.
        """
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset:
            return None

        if asset.status != AssetStatus.PENDING:
            raise ValueError(
                f"Asset is not in PENDING status. Current status: {asset.status}"
            )

        update_data = final_data or {}
        update_data["status"] = AssetStatus.AVAILABLE

        return await self.asset_repo.update(asset_id, update_data)

    async def reject_asset(
        self, asset_id: UUID, reason: Optional[str] = None
    ) -> Optional[Asset]:
        """
        Rejects a pending asset.
        """
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset:
            return None

        if asset.status != AssetStatus.PENDING:
            raise ValueError(
                f"Asset is not in PENDING status. Current status: {asset.status}"
            )

        return await self.asset_repo.update(asset_id, {"status": AssetStatus.REJECTED})
