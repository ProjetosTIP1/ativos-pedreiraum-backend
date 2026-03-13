import asyncpg
from domain.entities import AppConfig
from domain.interfaces import IConfigRepository

CONFIG_COLUMNS = "key, value"


class SQLConfigRepository(IConfigRepository):
    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection

    async def get_config(self) -> AppConfig:
        query = f"SELECT {CONFIG_COLUMNS} FROM app_configs"
        rows = await self.connection.fetch(query)
        
        config_dict = {row["key"]: row["value"] for row in rows}
        return AppConfig.model_validate(config_dict)

    async def update_config(self, config: AppConfig) -> AppConfig:
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
