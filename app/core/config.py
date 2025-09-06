from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"), env_nested_delimiter="__"
    )

    # App
    APP_NAME: str = "FastAPI Clean Architecture"
    VERSION: str = "0.1.0"
    ENV: str = "dev"  # dev|staging|prod
    ENABLE_DOCS: bool = True
    # Internationalization (i18n)
    LANG: str = "en"  # e.g., 'en', 'ru'

    # API
    API_PREFIX: str = "/api"

    # Security
    SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MIN: int = 15
    REFRESH_TOKEN_EXPIRES_DAYS: int = 30
    TOKEN_ISSUER: str | None = "fastapi_app"
    TOKEN_AUDIENCE: str | None = "fastapi_clients"
    REQUIRE_HTTPS: bool = False

    # Database (PostgreSQL) — either provide full URL or parts below
    DATABASE_URL: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_NAME: str | None = None
    DB_DRIVER: str = "postgresql+psycopg"  # SQLAlchemy driver
    DB_ECHO: bool = False

    # Cache / Redis (optional) — either provide full URL or parts below
    REDIS_URL: str | None = None
    REDIS_HOST: str | None = None
    REDIS_PORT: int | None = None
    REDIS_DB: int | None = None
    REDIS_PASSWORD: str | None = None


@lru_cache
def get_settings() -> Settings:
    s = Settings()  # type: ignore[call-arg]

    # Compose DATABASE_URL if not explicitly set and parts are provided
    if not s.DATABASE_URL and any(
        [s.DB_HOST, s.DB_PORT, s.DB_USER, s.DB_PASSWORD, s.DB_NAME]
    ):
        userinfo = ""
        if s.DB_USER:
            userinfo = s.DB_USER
            if s.DB_PASSWORD:
                userinfo += f":{s.DB_PASSWORD}"
            userinfo += "@"
        host = s.DB_HOST or "localhost"
        port = f":{s.DB_PORT}" if s.DB_PORT else ""
        dbname = f"/{s.DB_NAME}" if s.DB_NAME else ""
        s.DATABASE_URL = f"{s.DB_DRIVER}://{userinfo}{host}{port}{dbname}"

    # Compose REDIS_URL if not explicitly set and parts are provided
    if not s.REDIS_URL and any(
        [s.REDIS_HOST, s.REDIS_PORT, s.REDIS_DB is not None, s.REDIS_PASSWORD]
    ):
        auth = ""
        if s.REDIS_PASSWORD:
            # username not used by default; add only password segment
            auth = f":{s.REDIS_PASSWORD}@"
        host = s.REDIS_HOST or "localhost"
        port = s.REDIS_PORT or 6379
        db = s.REDIS_DB if s.REDIS_DB is not None else 0
        s.REDIS_URL = f"redis://{auth}{host}:{port}/{db}"

    return s
