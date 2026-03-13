from datetime import datetime
from typing import List, Optional, Union, Annotated
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_validator
from .enums import AssetStatus, AssetCondition, AssetCategory, PartState


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
    Field(
        discriminator="category"
    ),  # This will be handled in a factory or custom validator
]


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
    status: AssetStatus
    price: Optional[float] = None
    description: str
    main_image: HttpUrl
    gallery: List[HttpUrl] = Field(default_factory=list)
    is_featured: bool = False
    view_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Polymorphic specifications stored in JSONB
    specifications: Optional[dict] = None

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
