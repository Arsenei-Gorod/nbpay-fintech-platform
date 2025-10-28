from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"), env_nested_delimiter="__"
    )

    # App — базовые настройки приложения
    APP_NAME: str = "FastAPI Clean Architecture"  # имя приложения
    VERSION: str = "0.1.0"  # версия приложения
    ENV: str = "dev"  # окружение: dev|staging|prod
    ENABLE_DOCS: bool = True  # включить Swagger UI (документацию)
    # Internationalization (i18n)
    LANG: str = "en"  # язык локализации по умолчанию (например, 'en' или 'ru')

    # API — базовый префикс для всех маршрутов
    API_PREFIX: str = "/api"

    # Security — параметры безопасности
    SECRET_KEY: str = "change-me"  # секрет для подписи JWT (заменить в prod; >=32 символов)
    JWT_ALGORITHM: str = "HS256"  # алгоритм подписи JWT
    ACCESS_TOKEN_EXPIRES_MIN: int = 15  # срок жизни access-токена (мин)
    REFRESH_TOKEN_EXPIRES_DAYS: int = 30  # срок жизни refresh-токена (дни)
    TOKEN_ISSUER: str | None = "fastapi_app"  # значение iss в токене (источник)
    TOKEN_AUDIENCE: str | None = "fastapi_clients"  # значение aud (аудитория)
    REQUIRE_HTTPS: bool = False  # требовать HTTPS и отклонять HTTP-запросы
    TRUST_TOKEN_ROLE: bool = True  # доверять claim роли в токене (иначе — роль только из БД)
    PASSWORD_RESET_TOKEN_EXPIRES_MIN: int = 30  # срок жизни токена сброса пароля (мин)

    # Database (PostgreSQL) — либо указать полный URL, либо части ниже
    DATABASE_URL: str | None = None  # полный URL подключения к БД
    DB_HOST: str | None = None  # хост БД
    DB_PORT: int | None = None  # порт БД
    DB_USER: str | None = None  # пользователь БД
    DB_PASSWORD: str | None = None  # пароль БД
    DB_NAME: str | None = None  # имя базы данных
    DB_DRIVER: str = "postgresql+psycopg"  # драйвер SQLAlchemy
    DB_ECHO: bool = False  # логировать SQL-запросы (для разработки)

    # Cache / Redis (optional) — либо указать полный URL, либо части ниже
    REDIS_URL: str | None = None  # полный URL Redis
    REDIS_HOST: str | None = None  # хост Redis
    REDIS_PORT: int | None = None  # порт Redis
    REDIS_DB: int | None = None  # номер базы Redis
    REDIS_PASSWORD: str | None = None  # пароль Redis


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

    # Security hardening: forbid weak/default SECRET_KEY outside dev
    try:
        env = (s.ENV or "").lower()
    except Exception:
        env = "dev"
    if env != "dev":
        if not s.SECRET_KEY or s.SECRET_KEY == "change-me" or len(s.SECRET_KEY) < 32:
            raise ValueError(
                "Insecure SECRET_KEY. Set a strong SECRET_KEY (>=32 chars) for non-dev environments."
            )

    return s
