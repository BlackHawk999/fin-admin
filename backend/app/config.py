from __future__ import annotations

from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database (Render Postgres: DATABASE_URL; replace postgres:// with postgresql://)
    database_url: str = Field(
        default="postgresql://user:pass@localhost:5432/finadmin",
        validation_alias="DATABASE_URL",
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_postgres_url(cls, v):
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    # JWT
    secret_key: str = Field(default="change-me-in-production-use-env", validation_alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=60 * 24, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # ✅ ВАЖНО: делаем строкой, чтобы pydantic не пытался парсить как JSON list
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="CORS_ORIGINS",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        s = (self.cors_origins or "").strip()
        if not s:
            return []
        return [x.strip() for x in s.split(",") if x.strip()]

    # Timezone for exports
    timezone: str = Field(default="Asia/Tashkent", validation_alias="TIMEZONE")

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
