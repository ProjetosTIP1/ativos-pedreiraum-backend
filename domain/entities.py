from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from .enums import AssetStatus, AssetCondition, AssetCategory, UserRole, ImagePosition


class BaseEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class User(BaseEntity):
    id: UUID = Field(default_factory=uuid4)
    email: str = Field(..., regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    full_name: str = Field(..., min_length=2, max_length=100)
    contact: str = Field(..., min_length=10, max_length=20)
    role: UserRole = UserRole.REGULAR
    hashed_password: str = Field(..., min_length=60, max_length=60)  # Assuming bcrypt hash
    created_at: datetime = Field(default_factory=datetime.now)


class UserCreateRequest(BaseModel):
    email: str = Field(..., regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    full_name: str = Field(..., min_length=2, max_length=100)
    contact: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8)


class Category(BaseEntity):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=2, max_length=50)


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)


class ImageMetadata(BaseEntity):
    id: UUID = Field(default_factory=uuid4)
    asset_id: UUID = Field(..., description="ID of the associated asset")
    url: str = Field(..., min_length=5, max_length=255)
    is_main: bool = Field(default=False)
    position: ImagePosition = ImagePosition.OTHERS
    created_at: datetime = Field(default_factory=datetime.now)


class ImageUploadRequest(BaseModel):
    asset_id: UUID = Field(..., description="ID of the associated asset")
    url: str = Field(..., min_length=5, max_length=255)
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
    main_image: str = Field(..., min_length=5, max_length=255)
    highlighted: bool = Field(default=False)
    view_count: int = Field(default=0)
    created_by_user_id: Optional[UUID] = Field(None, description="ID of the user who created the asset")
    specifications: Optional[dict] = Field(None, description="Polymorphic specifications stored in JSONB")
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
    status: Optional[AssetStatus] = Field(AssetStatus.PENDING, description="Status of the asset")
    condition: AssetCondition
    price: Optional[float] = Field(None, ge=0)
    description: str = Field(..., min_length=10, max_length=1000)
    rep_contact: Optional[str] = Field(None, min_length=10, max_length=20, description="Whatsapp contact for the asset")
    main_image: str = Field(..., min_length=5, max_length=255)
    view_count: Optional[int] = Field(default=0)
    specifications: Optional[dict] = Field(None, description="Polymorphic specifications stored in JSONB")
    created_by_user_id: UUID = Field(..., description="ID of the user who created the asset")


class UpdateAssetRequest(BaseModel):
    id: UUID = Field(..., description="ID of the asset to update")
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[AssetCategory]
    subcategory: Optional[str] = Field(None, min_length=2, max_length=50)
    brand: Optional[str] = Field(None, min_length=2, max_length=50)
    model: Optional[str] = Field(None, min_length=2, max_length=50)
    year: Optional[int] = Field(None, ge=1900, le=datetime.now().year + 1)
    serial_number: Optional[str] = Field(None, min_length=2, max_length=50)
    location: Optional[str] = Field(None, min_length=2, max_length=100)
    status: Optional[AssetStatus] = Field(None, description="Status of the asset")
    condition: Optional[AssetCondition]
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    rep_contact: Optional[str] = Field(None, min_length=10, max_length=20, description="Whatsapp contact for the asset")
    main_image: Optional[str] = Field(None, min_length=5, max_length=255)
    highlighted: Optional[bool] = Field(None)
    specifications: Optional[dict] = Field(None, description="Polymorphic specifications stored in JSONB")