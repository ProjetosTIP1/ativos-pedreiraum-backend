import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Singleton class to manage the database connection pool.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )
            cls._instance.session_maker = async_sessionmaker(
                cls._instance.engine, expire_on_commit=False, class_=AsyncSession
            )
        return cls._instance

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, value):
        self._engine = value

    @property
    def session_maker(self):
        return self._session_maker

    @session_maker.setter
    def session_maker(self, value):
        self._session_maker = value

    async def close(self):
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection pool closed.")


# Dependency to get a session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    db_manager = DatabaseManager()
    async with db_manager.session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
