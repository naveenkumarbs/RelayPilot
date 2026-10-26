from functools import lru_cache
from pathlib import Path 
from typing import Literal 
from pydantic import Field, SecretStr, field_validator

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding = "utf-8",
        env_prefix = "RELAYPILOT_",
        extra = "ignore",
    )
    app_name: str = "RelayPilot API"
    app_version: str = "0.1.0"
    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    database_path: Path = Path("data/relaypilot.db")
    database_timeout_seconds: float = Field(default=10.0, gt=0)
    jwt_secret_key: SecretStr
    access_token_expire_minutes: int = Field(default=15, ge=1, le=60)
    jwt_issuer: str = "relaypilot"
    jwt_audience: str = "relaypilot-api"

    @property
    def resolved_database_path(self) -> Path: 
        path = self.database_path.expanduser()

        if not path.is_absolute():
            path = BACKEND_DIR / path 

        return path.resolve()

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < 32:
            raise ValueError("JWT secret must contain at least 32 characters.")
        return value

@lru_cache
def get_settings() -> Settings:
    return Settings()

