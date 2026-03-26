# Valemix Assets Catalog - Frontend Integration Guide

This guide provides the technical details required to integrate the frontend with the FastAPI backend, ensuring architectural consistency and type safety across both layers.

## 1. Authentication & Security

The system uses **HTTP-only Cookies** for secure session management.

### Mechanism
- **Login**: `POST /api/v1/auth/login`. On success, the server responds with a `Set-Cookie` header containing the `access_token`.
- **Security**: The cookie is marked as `HttpOnly` (preventing XSS access) and `SameSite=Lax`.
- **Automatic Handling**: The browser automatically includes this cookie in all subsequent requests to the backend domain.

### Frontend Implementation
- **CORS**: You **must** configure your HTTP client (Axios/Fetch) with `withCredentials: true`.
- **No Token Storage**: Do not attempt to store or read the token in `localStorage` or `sessionStorage`.
- **Role Checking**: Use the `user` object returned during login (or from a `/me` endpoint if implemented) to manage UI permissions.

---

## 2. Shared Domain Entities (TypeScript)

To maintain consistency with the Pydantic models in the backend, use these interfaces and enums.

### Enums
```typescript
export enum UserRole {
  ADMIN = "ADMIN",
  REGULAR = "REGULAR"
}

export enum AssetStatus {
  PENDING = "PENDING",
  AVAILABLE = "AVAILABLE",
  RESERVED = "RESERVED",
  SOLD = "SOLD",
  REJECTED = "REJECTED"
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

export enum PartState {
  NEW = "NEW",
  REFURBISHED = "REFURBISHED",
  USED = "USED"
}
```

### Interfaces
```typescript
export interface User {
  id: string; // UUID
  email: string;
  full_name: string;
  role: UserRole;
  created_at: string; // ISO DateTime
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

/** 
 * Polymorphic Specifications 
 * Stored in the 'specifications' field based on category.
 */
export interface TruckSpecs {
  mileage: number;
  traction: string;
  load_capacity: number;
  fuel_type: string;
}

export interface ExcavatorSpecs {
  operating_weight: number;
  power: number;
  hours: number;
  bucket_capacity?: number;
}

export interface PartSpecs {
  oem_code: string;
  compatible_equipment: string;
  part_state: PartState;
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
  specifications?: TruckSpecs | ExcavatorSpecs | PartSpecs | any;
}
```

---

## 3. Cross-Platform Validation (Zod)

We recommend using **Zod** on the frontend to mirror the backend's Pydantic validation. This ensures that data is valid before ever hitting the network.

**Example: Asset Validation Schema**
```typescript
import { z } from "zod";

export const assetSchema = z.object({
  name: z.string().min(3).max(100),
  year: z.number().int().min(1900).max(new Date().getFullYear() + 1),
  price: z.number().positive().optional(),
  category: z.nativeEnum(AssetCategory),
  // Add more as needed
});
```

---

## 4. API Endpoints Reference

Base URL: `/api/v1`

### Authentication (`/auth`)

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/login` | Public | Form data: `username` (email), `password`. Sets cookie. |
| `POST` | `/logout` | Public | Clears session cookie. |

### Public Assets (`/assets`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | List assets. Query: `category`, `brand`, `min_year`, `max_year`, `q`, `limit`, `offset`. |
| `GET` | `/highlights` | Returns featured assets. |
| `GET` | `/{slug}` | Returns detailed asset information by its slug. |

### Categories (`/categories`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | List all available categories and hierarchy. |

### Images (`/images`)

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/` | Auth | Upload image (multipart). Requires `asset_id`, `name`, `file`. |
| `GET` | `/asset/{id}`| Public | List all images for a specific asset. |
| `POST` | `/{id}/set-main`| Auth | Set specific image as main. Query: `asset_id`. |
| `PATCH`| `/{id}` | Auth | Update image metadata (JSON body). |
| `DELETE`|`/{id}` | Auth | Remove image and metadata. |

### Admin Operations (`/admin/assets`)
*All endpoints require Admin role.*

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/` | Create new asset. Initial status: `PENDING`. |
| `PATCH` | `/{id}` | Update asset details. |
| `POST` | `/{id}/approve` | Change status to `AVAILABLE`. Optional body to set final price. |
| `POST` | `/{id}/reject` | Change status to `REJECTED`. |
| `DELETE`| `/{id}` | Permanently remove asset. |

---

## 5. Error Handling

The API returns standard HTTP status codes. Errors include a descriptive JSON body:

- **401 Unauthorized**: Missing or invalid session cookie. Redirect to login.
- **403 Forbidden**: Authenticated but insufficient permissions (e.g., non-admin accessing `/admin`).
- **400 Bad Request**: Validation error. Check the `detail` field for specific messages.
- **404 Not Found**: Resource doesn't exist.

```json
{
  "detail": "Error message explanation here"
}
```
