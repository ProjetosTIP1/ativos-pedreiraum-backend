import asyncpg
from typing import AsyncGenerator, Optional
from .config import settings

from core.helpers.logger_helper import logger


class DatabaseManager:
    """
    Singleton class to manage the asyncpg connection pool.
    """

    _instance: Optional["DatabaseManager"] = None
    _pool: Optional[asyncpg.Pool] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    async def connect(self):
        """Initializes the connection pool."""
        if self._pool is None:
            try:
                self._pool = await asyncpg.create_pool(
                    user=settings.POSTGRES_USER,
                    password=settings.POSTGRES_PASSWORD,
                    database=settings.POSTGRES_DB,
                    host=settings.POSTGRES_HOST,
                    port=settings.POSTGRES_PORT,
                    min_size=5,
                    max_size=20,
                    max_queries=50000,
                    max_inactive_connection_lifetime=300.0,
                    timeout=30.0,
                )
                logger.info("Database connection pool created.")
            except Exception as e:
                logger.error(f"Failed to create database pool: {e}")
                raise

    async def disconnect(self):
        """Closes the connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            logger.info("Database connection pool closed.")

    async def get_connection(self) -> asyncpg.Connection:
        """Returns a connection from the pool."""
        if self._pool is None:
            await self.connect()

        if self._pool is None:
            raise Exception("Database pool is not initialized.")

        return self._pool.acquire()


# Dependency to get a connection from the pool
async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    FastAPI dependency to provide a database connection.
    Ensures the connection is released back to the pool after use.
    """
    db_manager = DatabaseManager()

    # Ensure pool is initialized (useful if first request hits here)
    if db_manager._pool is None:
        await db_manager.connect()

    if db_manager._pool is None:
        logger.error("Database pool could not be initialized.")
        raise Exception("Database connectivity error.")

    async with db_manager._pool.acquire() as connection:
        try:
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        # async with automatically releases the connection back to the pool
