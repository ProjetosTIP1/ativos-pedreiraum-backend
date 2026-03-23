from typing import List, Optional
from uuid import UUID
from passlib.context import CryptContext
from domain.entities import User, UserCreateRequest
from domain.interfaces import IUserRepository
from core.helpers.exceptions_helper import (
    ServiceException,
    ValidationServiceException,
    ConflictServiceException,
    InfrastructureServiceException,
)

# Password hashing configuration
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class UserService:
    def __init__(self, user_repo: IUserRepository):
        try:
            self.user_repo = user_repo
        except Exception as e:
            raise InfrastructureServiceException(
                "Failed to initialize user service"
            ) from e

    async def create_user(self, user_data: UserCreateRequest) -> User:
        try:
            # Check if user already exists
            existing = await self.user_repo.get_by_email(user_data.email)
            if existing:
                raise ConflictServiceException(
                    f"User with email {user_data.email} already exists."
                )

            # Hash password
            password = user_data.password
            hashed_password = pwd_context.hash(password)

            return await self.user_repo.create(user_data, hashed_password)
        except ServiceException:
            raise
        except ValueError as e:
            raise ValidationServiceException(str(e)) from e
        except Exception as e:
            raise InfrastructureServiceException("Failed to create user") from e

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        try:
            return await self.user_repo.get_by_id(user_id)
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to fetch user by id") from e

    async def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            return await self.user_repo.get_by_email(email)
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to fetch user by email") from e

    async def list_users(self) -> List[User]:
        try:
            return await self.user_repo.list_all()
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to list users") from e

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except ServiceException:
            raise
        except Exception as e:
            raise ValidationServiceException("Invalid password format") from e

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        try:
            # First check if user exists and get password hash
            password_hash = await self.user_repo.get_password_hash_by_email(email)
            if not password_hash:
                return None
            # Verify password
            if not await self.verify_password(password, password_hash):
                return None
            # Only fetch full user data if authentication succeeds
            return await self.user_repo.get_by_email(email)
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to authenticate user") from e

    async def update_user(self, user_id: UUID, user_data: dict) -> Optional[User]:
        try:
            if "password" in user_data:
                password = user_data.pop("password")
                user_data["hashed_password"] = pwd_context.hash(password)

            return await self.user_repo.update(user_id, user_data)
        except ServiceException:
            raise
        except ValueError as e:
            raise ValidationServiceException(str(e)) from e
        except Exception as e:
            raise InfrastructureServiceException("Failed to update user") from e

    async def delete_user(self, user_id: UUID) -> bool:
        try:
            return await self.user_repo.delete(user_id)
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to delete user") from e

    async def update_password(
        self, user_id: UUID, old_password: str, new_password: str
    ) -> bool:
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise ValidationServiceException("User not found")

            # Get password hash
            password_hash = await self.user_repo.get_password_hash_by_email(user.email)
            if not password_hash:
                raise InfrastructureServiceException("Failed to retrieve current password")

            # Verify old password
            if not await self.verify_password(old_password, password_hash):
                raise ValidationServiceException("Incorrect old password")

            # Hash and update new password
            hashed_new_password = pwd_context.hash(new_password)
            updated_user = await self.user_repo.update(
                user_id, {"hashed_password": hashed_new_password}
            )
            return updated_user is not None
        except ServiceException:
            raise
        except Exception as e:
            raise InfrastructureServiceException("Failed to update password") from e
