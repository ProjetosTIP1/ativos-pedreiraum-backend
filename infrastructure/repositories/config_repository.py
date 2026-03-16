import asyncpg
from domain.entities import AppConfig
from domain.interfaces import IConfigRepository
from core.helpers.logger_helper import logger

CONFIG_COLUMNS = "key, value"


class SQLConfigRepository(IConfigRepository):
    def __init__(self, connection: asyncpg.Connection):
        try:
            self.connection = connection
        except Exception as e:
            logger.error(f"Error initializing SQLConfigRepository: {e}")
            raise

    async def get_config(self) -> AppConfig:
        try:
            query = f"SELECT {CONFIG_COLUMNS} FROM app_configs"
            rows = await self.connection.fetch(query)

            config_dict = {row["key"]: row["value"] for row in rows}
            return AppConfig.model_validate(config_dict)
        except Exception as e:
            logger.error(f"Error fetching app config: {e}")
            raise

    async def update_config(self, config: AppConfig) -> AppConfig:
        try:
            config_data = config.model_dump()

            # We use UPSERT for each config key
            for key, value in config_data.items():
                query = """
                    INSERT INTO app_configs (key, value)
                    VALUES ($1, $2)
                    ON CONFLICT (key) DO UPDATE SET value = $2, updated_at = CURRENT_TIMESTAMP
                """
                await self.connection.execute(query, key, str(value))

            return config
        except Exception as e:
            logger.error(f"Error updating app config: {e}")
            raise
