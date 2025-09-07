from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_dir = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        frozen=True,
        env_file=env_dir / ".env",
        env_file_encoding="utf-8",
    )

    log_level: str = "DEBUG"
    fast_api_debug: bool = False


settings = Settings()
