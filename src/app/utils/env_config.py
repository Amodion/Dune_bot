from __future__ import annotations

from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")

    SERVICE_NAME: str = "dune-bot"
    SERVICE_VERSION: str = "0.2.0"
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "dune_bot.log"
    LOG_BACKUP_COUNT: int = 14
    LOG_ENABLE_FILE: bool = False
    API_V1_PREFIX: str = "/api/v1"
    HEALTH_MESSAGE: str = "Long Live The Fighters!"

    TELEGRAM_BOT_TOKEN: SecretStr | None = None
    TELEGRAM_WEBHOOK_PATH_SECRET: str = "local-dev-webhook"
    TELEGRAM_WEBHOOK_SECRET_TOKEN: SecretStr | None = None
    PUBLIC_BASE_URL: str | None = None

    @field_validator("LOG_FILE")
    @classmethod
    def validate_log_file(cls, value: str) -> str:
        if "/" in value or "\\" in value:
            raise ValueError("LOG_FILE must be a filename, not a path.")
        return value

    @field_validator("PUBLIC_BASE_URL")
    @classmethod
    def normalize_public_base_url(cls, value: str | None) -> str | None:
        if value is None or value.strip() == "":
            return None
        value = value.rstrip("/")
        if not value.startswith(("http://", "https://")):
            raise ValueError("PUBLIC_BASE_URL must start with http:// or https://.")
        return value

    @field_validator("TELEGRAM_WEBHOOK_PATH_SECRET")
    @classmethod
    def validate_path_secret(cls, value: str) -> str:
        if not value or "/" in value:
            raise ValueError("TELEGRAM_WEBHOOK_PATH_SECRET must be a non-empty path segment.")
        return value

    @property
    def telegram_bot_token_value(self) -> str | None:
        return self.TELEGRAM_BOT_TOKEN.get_secret_value() if self.TELEGRAM_BOT_TOKEN else None

    @property
    def telegram_webhook_secret_token_value(self) -> str | None:
        if self.TELEGRAM_WEBHOOK_SECRET_TOKEN is None:
            return None
        value = self.TELEGRAM_WEBHOOK_SECRET_TOKEN.get_secret_value()
        return value or None

    @property
    def webhook_url(self) -> str | None:
        if self.PUBLIC_BASE_URL is None:
            return None
        return f"{self.PUBLIC_BASE_URL}/telegram/webhook/{self.TELEGRAM_WEBHOOK_PATH_SECRET}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
