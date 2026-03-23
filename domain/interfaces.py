from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from .entities import (
    Asset,
    CreateAssetRequest,
    UpdateAssetRequest,
    Category,
    AppConfig,
    User,
    UserCreateRequest,
    Branch,
    ImageMetadata,
)
from .enums import AssetCategory, AssetStatus


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
        status: Optional[AssetStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Asset]:
        pass

    @abstractmethod
    async def get_featured(self) -> List[Asset]:
        pass

    @abstractmethod
    async def create(self, asset: CreateAssetRequest) -> Asset:
        pass

    @abstractmethod
    async def update(
        self, asset_id: UUID, asset_data: UpdateAssetRequest
    ) -> Optional[Asset]:
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


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_password_hash_by_email(self, email: str) -> Optional[str]:
        pass

    @abstractmethod
    async def list_all(self) -> List[User]:
        pass

    @abstractmethod
    async def create(self, user: UserCreateRequest, hashed_password: str) -> User:
        pass

    @abstractmethod
    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        pass


class IBranchRepository(ABC):
    @abstractmethod
    async def get_by_id(self, branch_id: int) -> Optional[Branch]:
        pass

    @abstractmethod
    async def list_all(self) -> List[Branch]:
        pass

    @abstractmethod
    async def create(self, branch: Branch) -> Branch:
        pass

    @abstractmethod
    async def update(self, branch_id: int, branch_data: dict) -> Optional[Branch]:
        pass

    @abstractmethod
    async def delete(self, branch_id: int) -> bool:
        pass


class IConfigRepository(ABC):
    @abstractmethod
    async def get_config(self) -> AppConfig:
        pass

    @abstractmethod
    async def update_config(self, config: AppConfig) -> AppConfig:
        pass


class IImageRepository(ABC):
    @abstractmethod
    async def get_by_id(self, image_id: UUID) -> Optional[ImageMetadata]:
        pass

    @abstractmethod
    async def list_by_asset(self, asset_id: UUID) -> List[ImageMetadata]:
        pass

    @abstractmethod
    async def create(self, image: ImageMetadata) -> ImageMetadata:
        pass

    @abstractmethod
    async def update(
        self, image_id: UUID, image_data: ImageMetadata
    ) -> Optional[ImageMetadata]:
        pass

    @abstractmethod
    async def delete(self, image_id: UUID) -> bool:
        pass

    @abstractmethod
    async def set_main_image(self, asset_id: UUID, image_id: UUID) -> bool:
        pass
