from functools import lru_cache
from pathlib import Path

from pydantic import computed_field, EmailStr, SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from expenses_tracker.core.constants import Environment
from expenses_tracker.core.utils import get_project_config

base_dir = Path(__file__).parent.parent.parent

project_config = get_project_config(base_dir=base_dir)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        env_file=base_dir / ".env",
        env_file_encoding="utf-8",
    )

    project_name: str = project_config.get("name", "")
    project_version: str = project_config.get("version", "")
    project_description: str = project_config.get("description", "")
    static_url_path: Path = base_dir / "static"

    environment: Environment = Environment.TEST
    log_level: str = "DEBUG"
    fast_api_debug: bool = False
    enable_profiling: bool = False

    app_host: str = "127.0.0.1"
    app_port: int = 8000

    sentry_dsn: str = Field(default="")
    sentry_traces_sample_rate: float = 0.2
    sentry_profiles_sample_rate: float = 0.1

    otel_enabled: bool = True
    otel_endpoint: str = "localhost:4318"
    otel_service_name: str = "expenses-tracker"

    secret_key: str = "super-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 3
    refresh_token_expire_days: int = 30
    email_verification_token_expire_hours: int = 1
    password_reset_token_expire_hours: int = 1
    clock_skew_seconds: int = 180

    google_client_id: str = "google-client-id"
    google_client_secret: str = "google-client-secret"
    github_client_id: str = "github-client-id"
    github_client_secret: str = "github-client"

    domain: str = "localhost:8000"
    email_password: SecretStr = SecretStr("")
    sender_email: EmailStr = "sender_email@gmail.com"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587

    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "expenses_tracker"

    database_echo: bool = False
    database_pool_echo: bool = False
    pool_size: int = 50

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    user_dto_ttl_seconds: int = 60 * 30
    budget_dto_ttl_seconds: int = 60 * 30
    budgets_list_ttl_seconds: int = 60 * 30
    expense_dto_ttl_seconds: int = 60 * 30
    expenses_list_ttl_seconds: int = 60 * 30
    category_dto_ttl_seconds: int = 60 * 30
    categories_list_ttl_seconds: int = 60 * 30

    minio_public_endpoint: str = "https://storage.example.com"
    minio_root_user: str = "minio"
    minio_root_password: str = "minio123"
    minio_avatar_bucket: str = "avatars"

    @computed_field  # type: ignore
    @property
    def redis_dsn(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

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
            f"postgresql://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
