from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Single source of truth.

    Reads values from environment variables (and optional .env file),
    applies defaults, and validates types early at the startup.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Common
    app_name: str = Field(default="contacts-parser", validate_alias="APP_NAME")
    env: Literal["dev", "test", "prod"] = Field(default="dev", validation_alias="ENV")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # HTTP behavior
    http_timeout_seconds: float = Field(default=5.0, validation_alias="HTTP_TIMEOUT_SECONDS")
    http_max_retries: int = Field(default=3, validation_alias="HTTP_MAX_RETRIES")
    http_backoff_seconds: float = Field(default=0.2, validation_alias="HTTP_BACKOFF_SECONDS")
    http_user_agent: str = Field(default="contacts-parser/0.1", validation_alias="HTTP_USER_AGENT")
    http_min_delay_seconds: float = Field(default=0.0, validation_alias="HTTP_MIN_DELAY_SECONDS")
    pool_connections: int = Field(default=10, validation_alias="POOL_CONNECTIONS")
    pool_maxsize: int = Field(default=10, validation_alias="POOL_MAXSIZE")
    lru_maxsize: int = Field(default=1, validation_alias="LRU_MAXSIZE")

    # Parser settings
    parser_type: str = Field(default="html.parser", validation_alias="PARSER_TYPE")
    max_pages_deep: int = Field(default=1000, validation_alias="MAX_PAGES_DEEP")
    crawler_max_workers: int = Field(default=8, validation_alias="CRAWLER_MAX_WORKERS")

    @field_validator("http_timeout_seconds", "http_backoff_seconds")
    @classmethod
    def positive_floats(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Timeout/backoff must be > 0")
        return v

    @field_validator("http_min_delay_seconds")
    @classmethod
    def non_negative_floats(cls, v: float) -> float:
        if v < 0:
            raise ValueError("HTTP min delay must be >= 0")
        return v

    @field_validator("http_max_retries", "lru_maxsize", "max_pages_deep")
    @classmethod
    def non_negative_ints(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Max retries/lru maxsize/max pages deep must be >= 0")
        return v

    @field_validator("crawler_max_workers")
    @classmethod
    def positive_workers(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Crawler max workers must be > 0")
        return v


settings = Settings()
