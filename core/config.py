from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DEBUG: bool = Field(default=False)
    DEVELOPMENT_ENV: bool = Field(default=False)

    # Database
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="valemix")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: str = Field(default="5432")

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
    SECRET_KEY: str = Field(default="your-super-secret-key-change-it-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Local Storage
    UPLOAD_DIR: str = Field(default="uploads")

    # Application
    APP_NAME: str = "Valemix Assets Catalog"
    ALLOWED_ORIGINS: List[str] = ["*"]
    ADMIN_WHATSAPP: str = "5500000000000"


settings = Settings()
