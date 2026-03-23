import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DEBUG: bool = bool(os.getenv("DEBUG", False))
    DEVELOPMENT_ENV: bool = bool(os.getenv("DEVELOPMENT_ENV", False))

    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "valemix")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    DATABASE_URL: Optional[str] = Field(default=None)

    @property
    def ASYNCPG_URL(self) -> str:
        from urllib.parse import quote_plus

        if self.DATABASE_URL:
            # If a full URL is provided, ensure it's compatible with asyncpg
            return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

        # Construct from individual parts with encoded password
        encoded_password = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql://{self.POSTGRES_USER}:{encoded_password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # JWT
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "your-super-secret-key-change-it-in-production"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24)
    )  # 1 day

    # Local Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "images")

    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Valemix Assets Catalog")
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    ADMIN_WHATSAPP: str = os.getenv("ADMIN_WHATSAPP", "5500000000000")


settings = Settings()
