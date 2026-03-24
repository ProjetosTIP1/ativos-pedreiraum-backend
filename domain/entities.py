from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from .enums import AssetStatus, AssetCondition, AssetCategory, UserRole, ImagePosition


class BaseEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Placeholder entities for future implementation
class Branch(BaseEntity):
    id: int
    name: str
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class AppConfig(BaseEntity):
    id: int
    key: str
    value: str
    created_at: datetime = Field(default_factory=datetime.now)


class User(BaseEntity):
    id: UUID = Field(default_factory=uuid4)
    email: str = Field(...)
    full_name: str = Field(..., min_length=2, max_length=100)
    contact: str = Field(..., min_length=10, max_length=20)
    role: UserRole = UserRole.REGULAR
    created_at: datetime = Field(default_factory=datetime.now)


class UserCreateRequest(BaseModel):
    email: str = Field(...)
    full_name: str = Field(..., min_length=2, max_length=100)
    contact: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8)
    role: Optional[UserRole] = UserRole.REGULAR


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    contact: Optional[str] = Field(None, min_length=10, max_length=20)


class AdminUserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    contact: Optional[str] = Field(None, min_length=10, max_length=20)
    role: Optional[UserRole] = None
    email: Optional[str] = None


class UserUpdatePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class Category(BaseEntity):
    id: int
    name: str = Field(..., min_length=2, max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class ImageMetadata(BaseEntity):
    id: UUID = Field(default_factory=uuid4)
    asset_id: UUID = Field(..., description="ID of the associated asset")
    url: str = Field(..., min_length=5)
    is_main: bool = Field(default=False)
    position: ImagePosition = ImagePosition.OTHERS
    created_at: datetime = Field(default_factory=datetime.now)


class ImageUploadRequest(BaseModel):
    asset_id: UUID = Field(..., description="ID of the associated asset")
    is_main: bool = Field(default=False)
    position: ImagePosition = ImagePosition.OTHERS


class Asset(BaseEntity):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=2, max_length=100)
    category: AssetCategory
    subcategory: str = Field(..., min_length=2, max_length=50)
    brand: str = Field(..., min_length=2, max_length=50)
    model: str = Field(..., min_length=2, max_length=50)
    year: int = Field(..., ge=1900, le=datetime.now().year + 1)
    serial_number: str = Field(..., min_length=2, max_length=50)
    location: str = Field(..., min_length=2, max_length=100)
    condition: AssetCondition
    status: AssetStatus = AssetStatus.PENDING
    price: Optional[float] = Field(None, ge=0)
    description: str = Field(..., min_length=10, max_length=1000)
    highlighted: bool = Field(default=False)
    view_count: int = Field(default=0)
    created_by_user_id: Optional[UUID] = Field(
        None, description="ID of the user who created the asset"
    )
    specifications: Optional[dict] = Field(
        None, description="Polymorphic specifications stored in JSONB"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CreateAssetRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category: AssetCategory
    subcategory: str = Field(..., min_length=2, max_length=50)
    brand: str = Field(..., min_length=2, max_length=50)
    model: str = Field(..., min_length=2, max_length=50)
    year: int = Field(..., ge=1900, le=datetime.now().year + 1)
    serial_number: str = Field(..., min_length=2, max_length=50)
    location: str = Field(..., min_length=2, max_length=100)
    status: Optional[AssetStatus] = Field(
        AssetStatus.PENDING, description="Status of the asset"
    )
    condition: AssetCondition
    price: Optional[float] = Field(None, ge=0)
    description: str = Field(..., min_length=10, max_length=1000)
    rep_contact: Optional[str] = Field(
        None, min_length=10, max_length=20, description="Whatsapp contact for the asset"
    )
    view_count: Optional[int] = Field(default=0)
    highlighted: Optional[bool] = Field(default=False)
    specifications: Optional[dict] = Field(
        None, description="Polymorphic specifications stored in JSONB"
    )
    created_by_user_id: Optional[UUID] = Field(
        None, description="ID of the user who created the asset"
    )


class UpdateAssetRequest(BaseModel):
    id: Optional[UUID] = Field(None, description="ID of the asset to update")
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[AssetCategory] = None
    subcategory: Optional[str] = Field(None, min_length=2, max_length=50)
    brand: Optional[str] = Field(None, min_length=2, max_length=50)
    model: Optional[str] = Field(None, min_length=2, max_length=50)
    year: Optional[int] = Field(None, ge=1900, le=datetime.now().year + 1)
    serial_number: Optional[str] = Field(None, min_length=2, max_length=50)
    location: Optional[str] = Field(None, min_length=2, max_length=100)
    status: Optional[AssetStatus] = Field(None, description="Status of the asset")
    highlighted: Optional[bool] = Field(None)
    condition: Optional[AssetCondition] = Field(None)
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    rep_contact: Optional[str] = Field(
        None, min_length=10, max_length=20, description="Whatsapp contact for the asset"
    )
