from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "To-Do API"
    app_description: str = "Portfolio-ready REST API for task management."
    environment: str = "development"
    database_url: str = "sqlite:///./tasks.db"
    jwt_secret_key: str = Field(default="change-me-in-production")
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
