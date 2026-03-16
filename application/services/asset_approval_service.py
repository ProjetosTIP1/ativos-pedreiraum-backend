from uuid import UUID
from typing import Optional
from domain.entities import Asset
from domain.enums import AssetStatus
from domain.interfaces import IAssetRepository
from core.helpers.exceptions_helper import (
    ServiceException,
    ValidationServiceException,
    InfrastructureServiceException,
)


class AssetApprovalService:
    def __init__(self, asset_repo: IAssetRepository):
        try:
            self.asset_repo = asset_repo
        except Exception as e:
            raise InfrastructureServiceException("Failed to initialize asset approval service") from e

    async def approve_asset(
        self, asset_id: UUID, final_data: Optional[dict] = None
    ) -> Optional[Asset]:
        """
        Approves an asset, optionally updating its details (price, etc.)
        and setting status to AVAILABLE.
        """
        try:
            asset = await self.asset_repo.get_by_id(asset_id)
            if not asset:
                return None

            if asset.status != AssetStatus.PENDING:
                raise ValidationServiceException(
                    f"Asset is not in PENDING status. Current status: {asset.status}"
                )

            update_data = final_data or {}
            update_data["status"] = AssetStatus.AVAILABLE

            return await self.asset_repo.update(asset_id, update_data)
        except ServiceException:
            raise
        except ValueError as e:
            raise ValidationServiceException(str(e)) from e
        except Exception as e:
            raise InfrastructureServiceException("Failed to approve asset") from e

    async def reject_asset(
        self, asset_id: UUID, reason: Optional[str] = None
    ) -> Optional[Asset]:
        """
        Rejects a pending asset.
        """
        try:
            asset = await self.asset_repo.get_by_id(asset_id)
            if not asset:
                return None

            if asset.status != AssetStatus.PENDING:
                raise ValidationServiceException(
                    f"Asset is not in PENDING status. Current status: {asset.status}"
                )

            return await self.asset_repo.update(asset_id, {"status": AssetStatus.REJECTED})
        except ServiceException:
            raise
        except ValueError as e:
            raise ValidationServiceException(str(e)) from e
        except Exception as e:
            raise InfrastructureServiceException("Failed to reject asset") from e
