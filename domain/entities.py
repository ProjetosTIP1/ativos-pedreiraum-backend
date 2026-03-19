from datetime import datetime
from typing import List, Optional, Union, Annotated
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict, field_validator
from .enums import AssetStatus, AssetCondition, AssetCategory, PartState, UserRole, ImagePosition


class BaseEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Specialized Specifications
class TruckSpecs(BaseEntity):
    mileage: int
    traction: str
    load_capacity: float
    fuel_type: str


class ExcavatorSpecs(BaseEntity):
    operating_weight: float
    power: int
    hours: int
    bucket_capacity: Optional[float] = None


class GraderSpecs(BaseEntity):
    operating_weight: float
    power: int
    hours: int
    blade_width: Optional[float] = None


class IndustrialSpecs(BaseEntity):
    production_capacity: float
    opening_size: str
    motor_power: str


class PartSpecs(BaseEntity):
    oem_code: str
    compatible_equipment: str
    part_state: PartState


# Union of all possible specifications
AssetSpecs = Annotated[
    Union[TruckSpecs, ExcavatorSpecs, GraderSpecs, IndustrialSpecs, PartSpecs],
    Field(discriminator="category"),
]


class User(BaseEntity):
    id: UUID = Field(default_factory=uuid4)
    email: str
    full_name: str
    role: UserRole = UserRole.REGULAR
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)


class Branch(BaseEntity):
    id: int
    name: str
    location: str
    contact_info: Optional[str] = None


class ImageMetadata(BaseEntity):
    id: UUID = Field(default_factory=uuid4)
    asset_id: UUID
    url: str
    name: str
    alt_text: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    is_main: bool = False
    position: ImagePosition = ImagePosition.OTHERS
    created_at: datetime = Field(default_factory=datetime.now)


class Asset(BaseEntity):
    id: UUID = Field(default_factory=uuid4)
    slug: str
    name: str
    category: AssetCategory
    subcategory: str
    brand: str
    model: str
    year: int
    serial_number: str
    location: str
    condition: AssetCondition
    status: AssetStatus = AssetStatus.PENDING
    price: Optional[float] = None
    description: str
    main_image: str
    gallery: List[str] = Field(default_factory=list)
    is_featured: bool = False
    view_count: int = 0
    branch_id: int
    created_by_user_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.now)

    # Polymorphic specifications stored in JSONB
    specifications: Optional[dict] = None

    @field_validator("specifications", mode="before")
    @classmethod
    def validate_specifications(cls, v):
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v or {}

    @field_validator("gallery", mode="before")
    @classmethod
    def validate_gallery(cls, v):
        if isinstance(v, str):
            # Handle possible string representation of postgres array or JSON
            if v.startswith("{") and v.endswith("}"):
                v = v[1:-1].split(",")
            else:
                import json

                try:
                    v = json.loads(v)
                except json.JSONDecodeError:
                    return []
        if isinstance(v, list):
            return [str(url).strip('"') for url in v if url]
        return []

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not v:
            raise ValueError("Slug cannot be empty")
        return v.lower().replace(" ", "-")


class Category(BaseEntity):
    id: int
    name: str
    slug: str
    parent_id: Optional[int] = None


class AppConfig(BaseEntity):
    whatsapp_number: str
    site_title: str
