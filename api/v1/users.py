import asyncpg
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from core.database import get_db_connection
from infrastructure.repositories.user_repository import SQLUserRepository
from application.services.user_service import UserService
from domain.entities import (
    User,
    UserCreateRequest,
    UserUpdateRequest,
    AdminUserUpdateRequest,
    UserUpdatePasswordRequest,
)
from api.v1.auth import get_current_user, get_current_admin
from core.helpers.exceptions_helper import ServiceException, to_http_exception

router = APIRouter(prefix="/users", tags=["Users"])


async def get_user_service(
    conn: asyncpg.Connection = Depends(get_db_connection),
) -> UserService:
    repo = SQLUserRepository(conn)
    return UserService(repo)


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreateRequest,
    user_service: UserService = Depends(get_user_service),
    admin: User = Depends(get_current_admin),
):
    """Admin only: Create a new user."""
    try:
        return await user_service.create_user(body)
    except ServiceException as e:
        raise to_http_exception(e)


@router.get("/", response_model=List[User])
async def list_users(
    user_service: UserService = Depends(get_user_service),
    admin: User = Depends(get_current_admin),
):
    """Admin only: List all users."""
    try:
        return await user_service.list_users()
    except ServiceException as e:
        raise to_http_exception(e)


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return current_user


@router.patch("/me", response_model=User)
async def update_me(
    body: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """Update own profile."""
    try:
        # Exclude unset values to support partial updates
        update_data = body.model_dump(exclude_unset=True)
        return await user_service.update_user(current_user.id, update_data)
    except ServiceException as e:
        raise to_http_exception(e)


@router.patch("/me/password")
async def update_password(
    body: UserUpdatePasswordRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """Update own password."""
    try:
        success = await user_service.update_password(
            current_user.id, body.old_password, body.new_password
        )
        if success:
            return {"message": "Password updated successfully"}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update password"
        )
    except ServiceException as e:
        raise to_http_exception(e)


@router.patch("/{user_id}", response_model=User)
async def admin_update_user(
    user_id: UUID,
    body: AdminUserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    admin: User = Depends(get_current_admin),
):
    """Admin only: Update any user field (including role/email)."""
    try:
        update_data = body.model_dump(exclude_unset=True)
        return await user_service.update_user(user_id, update_data)
    except ServiceException as e:
        raise to_http_exception(e)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    admin: User = Depends(get_current_admin),
):
    """Admin only: Delete a user."""
    try:
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return None
    except ServiceException as e:
        raise to_http_exception(e)
