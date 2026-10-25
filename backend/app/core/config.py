from functools import lru_cache
from pathlib import Path 
from typing import Literal 
from pydantic import Field

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

    @property
    def resolved_database_path(self) -> Path: 
        path = self.database_path.expanduser()

        if not path.is_absolute():
            path = BACKEND_DIR / path 

        return path.resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()