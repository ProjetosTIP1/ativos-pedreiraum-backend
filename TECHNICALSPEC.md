Backend Specification: Valemix Assets API
1. Technical Stack
Language/Framework: Python 3.11+ / FastAPI
Validation: Pydantic v2
Database: PostgreSQL (with asyncpg for non-blocking I/O)
Auth: JWT (JSON Web Tokens) for Admin access
Storage: Cloudinary API integration for image management
2. Database Schema (Relational)
Table assets:
UUID primary key.
specifications: JSONB column (to store polymorphic data like HP, hours, mileage).
search_vector: tsvector (for Full-Text Search performance).
Table categories: ID, Name, Slug, ParentID (for subcategories).
Table configs: Global WhatsApp number and site settings.
3. API Endpoints (RESTful)
Public API (Client Facing)
GET /api/v1/assets: List assets with query params (category, brand, min_year, max_year, q).
GET /api/v1/assets/{slug}: Get full detail + increments view_count.
GET /api/v1/highlights: Returns featured assets for the home banner.
Admin API (Protected)
POST /api/v1/admin/assets: Create new asset.
PATCH /api/v1/admin/assets/{id}: Update fields (status, price, etc).
DELETE /api/v1/admin/assets/{id}: Delete asset (protected by business rules).
GET /api/v1/admin/stats: Aggregate data for the dashboard.
4. Key Logic: Polymorphic Validation
The backend must validate specifications based on the category field using Pydantic Discriminated Unions.
If category is TRUCKS, require mileage and traction.
If category is EXCAVATORS, require hours and operating_weight.
5. Security & Performance
CORS: Restricted to the frontend domain.
Rate Limiting: Protect the WhatsApp click incrementer.
Atomic Updates: Use UPDATE assets SET view_count = view_count + 1 to avoid race conditions.