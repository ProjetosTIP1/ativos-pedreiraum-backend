Domain Specification: Valemix Assets Catalog

This document defines the core business entities and rules for the Valemix Assets Catalog. These definitions serve as the "Single Source of Truth" for both the Backend (FastAPI/Pydantic) and Frontend (React/Zod).

1. Core Enums (Value Objects)

Standardizing status and condition codes to prevent data inconsistency.

AssetStatus: AVAILABLE | RESERVED | SOLD

AssetCondition: EXCELLENT | GOOD | REGULAR

AssetCategory:

TRUCKS (Caminhões)

EXCAVATORS (Escavadeiras/Retro)

CRUSHERS (Britadores/Peneiras)

GRADERS (Motoniveladoras/Compactadores)

PLANT (Correias/Equip. Planta)

PARTS (Peças/Componentes)

OTHER

2. The Base Asset Entity

Every asset, regardless of category, must contain these core fields.

Field

Type

Description

id

UUID

Unique identifier

slug

String

URL-friendly name (e.g., "escavadeira-cat-336-2018")

name

String

Commercial name

category

AssetCategory

Primary classification

subcategory

String

Specific type (e.g., "Basculante")

brand

String

Manufacturer (Caterpillar, Volvo, etc)

model

String

Model designation

year

Integer

Manufacturing year

serialNumber

String

Unique hardware ID

location

String

City/State (e.g., "Ipatinga/MG")

condition

AssetCondition

Physical state

status

AssetStatus

Commercial availability

price

Decimal?

Nullable (if null, show "Consultar")

description

Text

Free-form details

mainImage

String (URL)

Primary thumbnail

gallery

Array

List of image URLs

isFeatured

Boolean

Highlight in home banner

viewCount

Integer

Analytics counter

createdAt

DateTime

Audit timestamp

3. Specialized Specifications (Polymorphism)

Depending on the category, an asset will have an additional specifications object.

A. Heavy Machinery (Excavators / Graders)

operatingWeight: Float (tons)

power: Integer (HP/CV)

hours: Integer (Horímetro)

bucketCapacity: Float? (m³)

bladeWidth: Float? (m)

B. Vehicles (Trucks)

mileage: Integer (km)

traction: String (4x2, 6x4, etc)

loadCapacity: Float (tons)

fuelType: String

C. Industrial (Crushers / Plant)

productionCapacity: Float (t/h)

openingSize: String (mm)

motorPower: String (kW/HP)

D. Parts

oemCode: String

compatibleEquipment: String

partState: "NEW" | "REFURBISHED" | "USED"

4. WhatsApp Integration Logic

The message generator must follow this strict template to ensure lead quality:

Template:
Olá! Tenho interesse no [Name]. Categoria: [Category]. Marca/Modelo: [Brand] [Model]. Ano: [Year]. Link: [BaseURL]/ativos/[Slug]

5. Persistence Rules

No asset can be deleted if it has "RESERVED" status.

Every asset must have at least one image.

Slugs must be unique and automatically generated from name + year.
