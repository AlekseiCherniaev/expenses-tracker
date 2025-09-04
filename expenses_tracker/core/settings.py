from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, frozen=True)

    log_level: str = "INFO"
    fast_api_debug: bool = False


settings = Settings()
