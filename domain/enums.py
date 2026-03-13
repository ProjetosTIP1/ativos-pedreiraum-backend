from enum import Enum


class AssetStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"


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
