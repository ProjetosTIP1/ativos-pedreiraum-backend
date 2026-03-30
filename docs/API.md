# API Documentation - Valemix Assets Catalog

This document provides a comprehensive overview of the available API endpoints in the Valemix Assets Catalog backend.

**Base URL:** `/api/v1`

---

## Table of Contents
- [Authentication](#authentication)
- [Users](#users)
- [Assets](#assets)
- [Admin Assets](#admin-assets)
- [Categories](#categories)
- [Images](#images)

---

## Authentication

### POST `/auth/login`
Authenticates a user and sets an HTTP-only access cookie.

- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "message": "Logged in successfully",
    "user": { ...user_object }
  }
  ```
- **Requirements:** Public.

### POST `/auth/logout`
Clears the authentication cookie.

- **Response (200 OK):**
  ```json
  {
    "message": "Logged out successfully"
  }
  ```
- **Requirements:** Public.

---

## Users

### GET `/users/me`
Retrieve the currently authenticated user's profile.

- **Response (200 OK):** `User` object.
- **Requirements:** Authenticated user.

### PATCH `/users/me`
Update the current user's profile information.

- **Request Body:** `UserUpdateRequest`
  ```json
  {
    "full_name": "New Name",
    "contact": "3199999999"
  }
  ```
- **Response (200 OK):** Updated `User` object.
- **Requirements:** Authenticated user.

### PATCH `/users/me/password`
Update the current user's password.

- **Request Body:** `UserUpdatePasswordRequest`
  ```json
  {
    "old_password": "currentpassword",
    "new_password": "newsecurepassword"
  }
  ```
- **Response (200 OK):** Success message.
- **Requirements:** Authenticated user.

### GET `/users`
List all registered users.

- **Response (200 OK):** List of `User` objects.
- **Requirements:** Admin account only.

### POST `/users`
Create a new user manually.

- **Request Body:** `UserCreateRequest`
  ```json
  {
    "email": "newuser@example.com",
    "full_name": "New User",
    "contact": "3188888888",
    "password": "securepassword",
    "role": "REGULAR"
  }
  ```
- **Response (201 Created):** Created `User` object.
- **Requirements:** Admin account only.

### PATCH `/users/{user_id}`
Update any field of a specific user (including their role).

- **Request Body:** `AdminUserUpdateRequest`
  ```json
  {
    "role": "ADMIN",
    "full_name": "Updated Name"
  }
  ```
- **Response (200 OK):** Updated `User` object.
- **Requirements:** Admin account only.

### DELETE `/users/{user_id}`
Permanently delete a user.

- **Response (204 No Content):** Empty.
- **Requirements:** Admin account only.

---

## Assets

### GET `/assets/`
List all assets with optional filtering and pagination.

- **Query Parameters:**
  - `category`: `AssetCategory` (e.g. "CAMINHÕES")
  - `brand`: `str`
  - `min_year`: `int`
  - `max_year`: `int`
  - `limit`: `int` (default: 20)
  - `offset`: `int` (default: 0)
  - `user_id`: `UUID` (optional)
  - `status`: `AssetStatus` (default: 'DISPONÍVEL')
- **Response (200 OK):** List of `Asset` objects.
- **Requirements:** Public.

### GET `/assets/highlights`
Retrieve featured/highlighted assets.

- **Response (200 OK):** List of `Asset` objects.
- **Requirements:** Public.

### GET `/assets/{id}`
Retrieve detailed information about a single asset by ID.

- **Response (200 OK):** Detailed `Asset` object.
- **Requirements:** Public.

---

## Admin Assets

### POST `/admin/assets/`
Create a new asset.

- **Request Body:** `CreateAssetRequest`
- **Response (201 Created):** Created `Asset` object.
- **Requirements:** Admin account only.

### PATCH `/admin/assets/{asset_id}`
Partially update an existing asset.

- **Request Body:** `UpdateAssetRequest`
- **Response (200 OK):** Updated `Asset` object.
- **Requirements:** Admin account only.

### DELETE `/admin/assets/{asset_id}`
Remove an asset from the catalog.

- **Response (200 OK):**
  ```json
  {
    "message": "Asset deleted successfully"
  }
  ```
- **Requirements:** Admin account only.

---

## Categories

### GET `/categories/`
List all available asset categories.

- **Response (200 OK):** List of `Category` objects.
- **Requirements:** Public.

---

## Images

### GET `/images/asset/{asset_id}`
Retrieve all image metadata associated with a specific asset.

- **Response (200 OK):** List of `ImageMetadata`.
- **Requirements:** Public.

### POST `/images/`
Upload a new image for an asset.

- **Request Form-Data:**
  - `asset_id`: `UUID`
  - `position`: `str` (e.g. "FRENTE", "INTERIOR")
  - `is_main`: `bool`
  - `file`: `UploadFile`
- **Response (200 OK):** `ImageMetadata` object.
- **Requirements:** Authenticated user.

### GET `/images/{filename}`
Retrieve the raw image file.

- **Response (200 OK):** File stream.
- **Requirements:** Public.

### DELETE `/images/{image_id}`
Delete an image by ID.

- **Response (200 OK):**
  ```json
  {
    "message": "Image deleted successfully"
  }
  ```
- **Requirements:** Admin account only.

