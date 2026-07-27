from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    db_use_transaction_pooler: bool = False

    auth_jwt_secret: str
    auth_access_token_expire_minutes: int = 15
    auth_refresh_token_expire_days: int = 30

    environment: str = "local"
    api_v1_prefix: str = "/api/v1"

    # Comma-separated. Only matters for the Expo web target — native app
    # requests aren't subject to browser CORS. Defaults cover Metro's web
    # dev server ports (8081 current default, 19006 legacy).
    cors_allowed_origins: str = "http://localhost:8081,http://localhost:19006"

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # fields load from env/.env at runtime
