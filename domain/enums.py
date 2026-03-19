from enum import Enum


class AssetStatus(str, Enum):
    PENDING = "PENDING"
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    REJECTED = "REJECTED"


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    REGULAR = "REGULAR"


class AssetCondition(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    REGULAR = "REGULAR"


class AssetCategory(str, Enum):
    TRUCKS = "TRUCKS"
    EXCAVATORS = "EXCAVATORS"
    CRUSHERS = "CRUSHERS"
    GRADERS = "GRADERS"
    PLANT = "PLANT"
    PARTS = "PARTS"
    OTHER = "OTHER"


class PartState(str, Enum):
    NEW = "NEW"
    REFURBISHED = "REFURBISHED"
    USED = "USED"


class ImagePosition(str, Enum):
    FRONT = "FRONT"
    BACK = "BACK"
    SIDE_LEFT = "SIDE_LEFT"
    SIDE_RIGHT = "SIDE_RIGHT"
    INTERIOR = "INTERIOR"
    ENGINE = "ENGINE"
    TIRE = "TIRE"
    DASHBOARD = "DASHBOARD"
    OTHERS = "OTHERS"
