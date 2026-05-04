from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    environment: str = "dev"
    database_url: str = "sqlite:///./job_analytics.db"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    remotive_base_url: str = "https://remotive.com/api/remote-jobs"
    adzuna_base_url: str = "https://api.adzuna.com/v1/api/jobs"
    adzuna_app_id: str | None = None
    adzuna_app_key: str | None = None

    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    auth_cookie_name: str = "job_analytics_auth"
    auth_cookie_key: str = "change-me"
    auth_cookie_expiry_days: int = 7


@lru_cache
def get_settings() -> Settings:
    return Settings()
