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

    # MT5
    mt5_login: int | None = Field(default=None, alias="MT5_LOGIN")
    mt5_password: str | None = Field(default=None, alias="MT5_PASSWORD")
    mt5_server: str | None = Field(default=None, alias="MT5_SERVER")
    mt5_broker: str | None = Field(default=None, alias="MT5_BROKER")
    mt5_path: str | None = Field(
        default=r"C:\Program Files\MetaTrader 5\terminal64.exe",
        alias="MT5_PATH",
    )
    # Broker server clock vs UTC (hours). Many FX brokers: +2 winter / +3 summer.
    mt5_server_utc_offset_hours: float = Field(default=2.0, alias="MT5_SERVER_UTC_OFFSET_HOURS")

    # Data providers
    news_provider: str = Field(default="finnhub", alias="NEWS_PROVIDER")
    news_api_key: str | None = Field(default=None, alias="NEWS_API_KEY")
    fred_api_key: str | None = Field(default=None, alias="FRED_API_KEY")
    # Comma-separated FRED series IDs (W3·D2 defaults cover rates, dollar, labor, inflation).
    fred_series: str = Field(
        default="DFF,T10Y2Y,DTWEXBGS,CPIAUCSL,UNRATE,GDP",
        alias="FRED_SERIES",
    )

    # Alerts / email
    alert_channel: str = Field(default="resend", alias="ALERT_CHANNEL")
    resend_api_key: str | None = Field(default=None, alias="RESEND_API_KEY")
    email_from: str | None = Field(default=None, alias="EMAIL_FROM")
    email_alert_to: str | None = Field(default=None, alias="EMAIL_ALERT_TO")
    alert_telegram_bot_token: str | None = Field(default=None, alias="ALERT_TELEGRAM_BOT_TOKEN")
    alert_telegram_chat_id: str | None = Field(default=None, alias="ALERT_TELEGRAM_CHAT_ID")
    alert_webhook_url: str | None = Field(default=None, alias="ALERT_WEBHOOK_URL")

    # Auth — Clerk (humans)
    clerk_secret_key: str | None = Field(default=None, alias="CLERK_SECRET_KEY")
    clerk_jwks_url: str | None = Field(default=None, alias="CLERK_JWKS_URL")
    clerk_authorized_parties: str = Field(
        default="http://localhost:3000",
        alias="CLERK_AUTHORIZED_PARTIES",
    )
    clerk_allowed_org_id: str | None = Field(default=None, alias="CLERK_ALLOWED_ORG_ID")
    # Local/smoke only: HS256 secret when JWKS URL is empty
    clerk_test_jwt_secret: str | None = Field(default=None, alias="CLERK_TEST_JWT_SECRET")

    # Machine API keys (plaintext bootstrap → hashed into api_keys table)
    ouroboros_api_key_client: str | None = Field(default=None, alias="OUROBOROS_API_KEY_CLIENT")
    ouroboros_api_key_epg: str | None = Field(default=None, alias="OUROBOROS_API_KEY_EPG")
    ouroboros_api_key_quant: str | None = Field(default=None, alias="OUROBOROS_API_KEY_QUANT")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def fred_series_list(self) -> list[str]:
        return [s.strip().upper() for s in self.fred_series.split(",") if s.strip()]

    @property
    def clerk_authorized_parties_list(self) -> list[str]:
        return [p.strip() for p in self.clerk_authorized_parties.split(",") if p.strip()]

    def bootstrap_api_keys(self) -> list[tuple[str, str, str]]:
        """Return (name, service_name, raw_key) triples for non-empty env keys."""
        out: list[tuple[str, str, str]] = []
        mapping = (
            ("client", "client", self.ouroboros_api_key_client),
            ("epg", "epg", self.ouroboros_api_key_epg),
            ("quant", "quant", self.ouroboros_api_key_quant),
        )
        for name, service, raw in mapping:
            if raw and raw.strip():
                out.append((name, service, raw.strip()))
        return out


@lru_cache
def get_settings() -> Settings:
    return Settings()
