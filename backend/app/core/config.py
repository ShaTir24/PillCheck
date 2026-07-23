from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    db_use_transaction_pooler: bool = False

    supabase_jwt_secret: str = ""

    environment: str = "local"
    api_v1_prefix: str = "/api/v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # fields load from env/.env at runtime
