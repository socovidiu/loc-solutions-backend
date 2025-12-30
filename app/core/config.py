from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # ───────────────
    # App
    # ───────────────
    APP_NAME: str = "LocPortal Backend"
    APP_VERSION: str = "0.1.0"
    ENV: str = Field(default="dev", description="dev | staging | prod")

    # ───────────────
    # API / Server
    # ───────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ───────────────
    # Database
    # ───────────────
    DATABASE_URL: str = Field(
        ...,
        description="Database connection string"
    )

    # ───────────────
    # TMS Integration
    # ───────────────
    TMS_PROVIDER: str = Field(default="phrase")
    TMS_BASE_URL: str = Field(default="")
    TMS_API_TOKEN: str = Field(default="")

    TMS_PROJECT_ID: str = Field(
        ...,
        description="Default TMS project used for job creation"
    )

    # Webhooks
    TMS_WEBHOOK_SECRET: str = Field(default="")

    # ───────────────
    # LLM Integration
    # ───────────────
    LLM_PROVIDER: str = Field(default="openai")
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # ───────────────
    # HTTP behavior
    # ───────────────
    HTTP_TIMEOUT: int = 30
    HTTP_RETRIES: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
