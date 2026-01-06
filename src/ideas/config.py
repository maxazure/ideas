import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    app_name: str = "Idea Execution Loop"
    database_url: str = "sqlite+aiosqlite:///./ideas.db"
    debug: bool = False
    api_key: str = secrets.token_urlsafe(32)
    api_key_enabled: bool = False


settings = Settings()
