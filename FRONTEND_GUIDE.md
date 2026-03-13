# Valemix Assets Catalog - Frontend Integration Guide

This guide provides the necessary technical details to integrate the frontend with the FastAPI backend.

## 1. Authentication Mode

The system uses **HTTP-only Cookies** for token management.

- **Mechanism**: On successful login, the server sets a `Set-Cookie` header with the `access_token`.
- **Security**: The cookie is `HttpOnly`, `SameSite=Lax`, and should be `Secure` in production.
- **Client Handling**: The browser automatically sends the cookie with every request to the backend. **Do not** attempt to read the token from JavaScript.
- **CORS**: Ensure `withCredentials: true` is set in your HTTP client (Axios/Fetch).

---

## 2. Entities & TypeScript Interfaces

### Enums
```typescript
export enum AssetStatus {
  PENDING = "PENDING",
  AVAILABLE = "AVAILABLE",
  RESERVED = "RESERVED",
  SOLD = "SOLD",
  REJECTED = "REJECTED"
}

export enum UserRole {
  ADMIN = "ADMIN",
  REGULAR = "REGULAR"
}

export enum AssetCondition {
  EXCELLENT = "EXCELLENT",
  GOOD = "GOOD",
  REGULAR = "REGULAR"
}

export enum AssetCategory {
  TRUCKS = "TRUCKS",
  EXCAVATORS = "EXCAVATORS",
  CRUSHERS = "CRUSHERS",
  GRADERS = "GRADERS",
  PLANT = "PLANT",
  PARTS = "PARTS",
  OTHER = "OTHER"
}
```

### Core Entities
```typescript
export interface User {
  id: string; // UUID
  email: string;
  full_name: string;
  role: UserRole;
  created_at: string; // ISO Date
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  parent_id?: number;
}

export interface Branch {
  id: number;
  name: string;
  location: string;
  contact_info?: string;
}

export interface ImageMetadata {
  id: string; // UUID
  asset_id: string; // UUID
  url: string;
  name: string;
  alt_text?: string;
  content_type?: string;
  size?: number;
  width?: number;
  height?: number;
  is_main: boolean;
  created_at: string;
}

export interface Asset {
  id: string; // UUID
  slug: string;
  name: string;
  category: AssetCategory;
  subcategory: string;
  brand: string;
  model: string;
  year: number;
  serial_number: string;
  location: string;
  condition: AssetCondition;
  status: AssetStatus;
  price?: number;
  description: string;
  main_image: string; // URL
  gallery: string[]; // Array of URLs
  is_featured: boolean;
  view_count: number;
  branch_id: number;
  created_by_user_id?: string;
  created_at: string;
  specifications?: Record<string, any>;
}
```

---

## 3. API Endpoints

### Authentication (`/api/v1/auth`)

#### **POST /login**
Authenticates the user and sets the `access_token` cookie.
- **Request (Form Data)**:
  - `username`: Email
  - `password`: Password
- **Response (200 OK)**:
  ```json
  {
    "message": "Logged in successfully",
    "user": { ...UserEntity }
  }
  ```

#### **POST /logout**
Clears the session cookie.
- **Response (200 OK)**:
  ```json
  { "message": "Logged out successfully" }
  ```

---

### Public Assets (`/api/v1/assets`)

#### **GET /**
List assets with optional filters.
- **Query Parameters**:
  - `category`: `AssetCategory`
  - `brand`: string
  - `min_year`: number
  - `max_year`: number
  - `q`: string (Search query)
  - `limit`: number (default 20)
  - `offset`: number (default 0)
- **Response**: `Asset[]`

#### **GET /highlights**
Get featured assets for the homepage.
- **Response**: `Asset[]`

#### **GET /{slug}**
Get detailed information for a specific asset.
- **Response**: `Asset`

---

### Images (`/api/v1/images`)
*Requires Authentication for modifications*

#### **POST /**
Adds metadata for an image (alt text, name, dimensions).
- **Request Body**:
  - `asset_id`: string (UUID)
  - `url`: string
  - `name`: string
  - `alt_text`: string (optional)
  - `is_main`: boolean (default: false)
- **Response**: `ImageMetadata`

#### **GET /asset/{asset_id}**
List all images and metadata for a specific asset.
- **Response**: `ImageMetadata[]`

#### **POST /{image_id}/set-main**
Set an image as the main image for its asset. Automatically updates the asset's `main_image` field.
- **Query Parameters**: `asset_id` (UUID)
- **Response**: `{ "message": "Main image updated successfully" }`

#### **PATCH /{image_id}**
Update metadata for an image.
- **Request Body**: `Partial<ImageMetadata>`
- **Response**: `ImageMetadata`

#### **DELETE /{image_id}**
Delete an image's metadata.
- **Response**: `{ "message": "Image and metadata deleted successfully" }`

#### **GET /**
List all categories.
- **Response**: `Category[]`

---

### Admin Assets (`/api/v1/admin/assets`)
*Requires Admin Role / Session Cookie*

#### **POST /**
Submit a new asset.
- **Request Body**: `Partial<Asset>`
- **Response**: `Asset` (Initially set to `PENDING`)

#### **PATCH /{asset_id}**
Update an existing asset.
- **Request Body**: `Partial<Asset>`
- **Response**: `Asset`

#### **POST /{asset_id}/approve**
Admin workflow to approve an asset and make it visible.
- **Request Body**: Optional `{ "price": number, ... }`
- **Response**: `Asset` (Status changes to `AVAILABLE`)

#### **POST /{asset_id}/reject**
Admin workflow to reject an asset.
- **Response**: `Asset` (Status changes to `REJECTED`)

#### **DELETE /{asset_id}**
Delete an asset.
- **Response**: `{ "message": "Asset deleted successfully" }`
