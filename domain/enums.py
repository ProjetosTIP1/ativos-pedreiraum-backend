from enum import Enum


class AssetStatus(str, Enum):
    PENDING = "PENDENTE"
    AVAILABLE = "DISPONÍVEL"
    RESERVED = "RESERVADO"
    SOLD = "VENDIDO"
    REJECTED = "REJEITADO"


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    REGULAR = "REGULAR"


class AssetCondition(str, Enum):
    EXCELLENT = "EXCELENTE"
    GOOD = "BOM"
    REGULAR = "REGULAR"


class AssetCategory(str, Enum):
    TRUCKS = "CAMINHÕES"
    EXCAVATORS = "ESCAVADEIRAS"
    CRUSHERS = "BRITADORES"
    GRADERS = "MOTONIVELADORAS"
    PLANT = "PLANTA"
    PARTS = "PEÇAS"
    OTHER = "OUTROS"


class ImagePosition(str, Enum):
    FRONT = "FRENTE"
    BACK = "TRÁS"
    SIDE_LEFT = "LADO_ESQUERDO"
    SIDE_RIGHT = "LADO_DIREITO"
    INTERIOR = "INTERIOR"
    ENGINE = "MOTOR"
    TIRE = "PNEU"
    DASHBOARD = "PAINEL"
    OTHERS = "OUTROS"
