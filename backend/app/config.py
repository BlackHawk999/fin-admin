from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database (Render Postgres: DATABASE_URL; replace postgres:// with postgresql://)
    database_url: str = "postgresql://user:pass@localhost:5432/finadmin"

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_postgres_url(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    # JWT
    secret_key: str = "change-me-in-production-use-env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # CORS
    # Можно задавать:
    # 1) JSON: ["https://a.com","https://b.com"]
    # 2) строкой через запятую: https://a.com,https://b.com
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if v is None:
            return v

        # Если уже список — ок
        if isinstance(v, list):
            return v

        # Если строка: "a,b,c"
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return []
            return [x.strip() for x in s.split(",") if x.strip()]

        return v

    # Timezone for exports
    timezone: str = "Asia/Tashkent"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
