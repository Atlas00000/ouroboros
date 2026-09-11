"""Environment-driven settings (12-factor)."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="local", alias="APP_ENV")
    app_name: str = Field(default="ouroboros-server", alias="APP_NAME")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(
        default="postgresql://ouroboros:ouroboros@localhost:5433/ouroboros",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6380/0", alias="REDIS_URL")

    sentry_dsn_server: str | None = Field(default=None, alias="SENTRY_DSN_SERVER")

    cors_origins: str = Field(
        default="http://localhost:3000",
        alias="CORS_ORIGINS",
        description="Comma-separated allowed origins.",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
