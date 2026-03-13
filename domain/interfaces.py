from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from .entities import Asset, Category, AppConfig
from .enums import AssetCategory


class IAssetRepository(ABC):
    @abstractmethod
    async def get_by_id(self, asset_id: UUID) -> Optional[Asset]:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Asset]:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def get_featured(self) -> List[Asset]:
        pass

    @abstractmethod
    async def create(self, asset: Asset) -> Asset:
        pass

    @abstractmethod
    async def update(self, asset_id: UUID, asset_data: dict) -> Optional[Asset]:
        pass

    @abstractmethod
    async def delete(self, asset_id: UUID) -> bool:
        pass

    @abstractmethod
    async def increment_view_count(self, asset_id: UUID) -> None:
        pass


class ICategoryRepository(ABC):
    @abstractmethod
    async def list_all(self) -> List[Category]:
        pass

    @abstractmethod
    async def get_by_id(self, category_id: int) -> Optional[Category]:
        pass


class IConfigRepository(ABC):
    @abstractmethod
    async def get_config(self) -> AppConfig:
        pass

    @abstractmethod
    async def update_config(self, config: AppConfig) -> AppConfig:
        pass
