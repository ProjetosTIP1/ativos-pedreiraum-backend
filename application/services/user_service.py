from typing import List, Optional
from uuid import UUID
from passlib.context import CryptContext
from domain.entities import User
from domain.interfaces import IUserRepository
from domain.enums import UserRole

# Password hashing configuration
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def create_user(self, user_data: dict) -> User:
        # Check if user already exists
        existing = await self.user_repo.get_by_email(user_data["email"])
        if existing:
            raise ValueError(f"User with email {user_data['email']} already exists.")

        # Hash password
        password = user_data.pop("password")
        user_data["hashed_password"] = pwd_context.hash(password)

        user = User.model_validate(user_data)
        return await self.user_repo.create(user)

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.user_repo.get_by_email(email)

    async def list_users(self) -> List[User]:
        return await self.user_repo.list_all()

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def update_user(self, user_id: UUID, user_data: dict) -> Optional[User]:
        if "password" in user_data:
            password = user_data.pop("password")
            user_data["hashed_password"] = pwd_context.hash(password)
        
        return await self.user_repo.update(user_id, user_data)

    async def delete_user(self, user_id: UUID) -> bool:
        return await self.user_repo.delete(user_id)
