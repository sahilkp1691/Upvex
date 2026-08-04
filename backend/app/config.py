from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """Supabase/Railway paste often uses postgresql://; async engine needs +asyncpg."""
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Core
    app_name: str = "Upvex"
    app_env: str = "development"  # development | production
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    # Database — Supabase Postgres in prod/dev-with-keys, local Postgres otherwise
    database_url: str = "postgresql+asyncpg://upvex:upvex@localhost:5432/upvex"

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_db_url(cls, v: object) -> object:
        if isinstance(v, str):
            return normalize_database_url(v.strip())
        return v

    # Supabase Auth
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_jwt_secret: str = ""  # legacy HS256 secret; if empty, JWKS (RS256/ES256) is used

    # Dev-mode auth bypass: any request without a Bearer token acts as a local dev user.
    # NEVER enable in production.
    dev_auth_bypass: bool = False

    # Celery / Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_task_always_eager: bool = False  # run tasks inline (no worker/redis needed) for local dev

    # OpenRouter — model per task type (cost/quality tunable independently)
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    model_lesson_generation: str = "anthropic/claude-sonnet-4.5"
    model_quiz_generation: str = "anthropic/claude-sonnet-4.5"
    model_diagnostic_evaluator: str = "openai/gpt-4.1-mini"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def sync_database_url(self) -> str:
        """Database URL for synchronous contexts (Celery workers)."""
        return self.database_url.replace("+asyncpg", "+psycopg2")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
