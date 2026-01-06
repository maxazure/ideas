from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    app_name: str = "Idea Execution Loop"
    database_url: str = "sqlite+aiosqlite:///./ideas.db"
    debug: bool = False


settings = Settings()
