from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from expenses_tracker.core.constants import Environment
from expenses_tracker.core.utils import get_project_config

base_dir = Path(__file__).parent.parent.parent

project_config = get_project_config(base_dir=base_dir)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        frozen=True,
        extra="ignore",
        env_file=base_dir / ".env",
        env_file_encoding="utf-8",
    )

    project_name: str = project_config.get("name", "")
    project_version: str = project_config.get("version", "")
    project_description: str = project_config.get("description", "")

    environment: Environment = Environment.DEV
    log_level: str = "DEBUG"
    fast_api_debug: bool = False

    app_host: str = "127.0.0.1"
    app_port: int = 8000

    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "expenses_tracker"

    @computed_field  # type: ignore
    @property
    def async_postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    @computed_field  # type: ignore
    @property
    def sync_postgres_url(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )


settings = Settings()
