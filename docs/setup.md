# Быстрый старт

## Требования
- Python 3.11+
- UV (Astral)
- Docker Compose (для dev-окружения)

## Установка backend
```
uv venv
uv sync
cp .env.example .env
```

## Запуск (локально)
```
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

Документация API: http://localhost:8000/docs

## Запуск (Docker, dev профиль)
```
docker compose --profile dev up -d --build
```

- backend: http://localhost:8000
- frontend: http://localhost:5173
- CloudBeaver: http://localhost:8978 (admin/admin)

## Переменные окружения (основные)
- `LANG` — язык сообщений (`en` или `ru`).
- `API_PREFIX` — префикс API (по умолчанию `/api`).
- `SECRET_KEY` — секрет для JWT (в prod должен быть ≥ 32 символов; в non‑dev слабый ключ запрещён).
- `JWT_ALGORITHM` — алгоритм подписи (по умолчанию HS256).
- `ACCESS_TOKEN_EXPIRES_MIN` — срок жизни access (мин).
- `REFRESH_TOKEN_EXPIRES_DAYS` — срок жизни refresh (дни).
- `TOKEN_ISSUER`/`TOKEN_AUDIENCE` — рекомендуется в проде для строгой валидации `iss`/`aud`.
- `REQUIRE_HTTPS` — отклонять HTTP‑запросы (включайте в проде).
- `TRUST_TOKEN_ROLE` — доверять ли роли из клейма токена (в проде рекомендуем `false`).
- `DATABASE_URL` или `DB_*` — параметры подключения к БД.
- `REDIS_URL` или `REDIS_*` — параметры подключения к Redis.

См. `.env.example` для полного списка.

## Сборка документации
```
uv run mkdocs serve -a 0.0.0.0:8001   # dev-сервер доков
# или
uv run mkdocs build                    # сборка в каталог site/
```

## Рекомендуемая конфигурация для продакшена

Ниже пример `.env` для боевого окружения. Адаптируйте под свою инфраструктуру.

```
# Общие
APP_NAME="My App"
ENV="prod"                 # включает строгие проверки безопасности
ENABLE_DOCS=false           # опционально выключить Swagger в проде
LANG="en"
API_PREFIX="/api"

# Безопасность
SECRET_KEY="CHANGE-TO-LONG-RANDOM-STRING-AT-LEAST-32-CHARS"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRES_MIN=15
REFRESH_TOKEN_EXPIRES_DAYS=30
TOKEN_ISSUER="my_app"
TOKEN_AUDIENCE="my_clients"
REQUIRE_HTTPS=true          # отклонять HTTP-запросы
TRUST_TOKEN_ROLE=false      # роль берётся только из БД

# База данных (пример для PostgreSQL)
DATABASE_URL="postgresql+psycopg://user:pass@db:5432/appdb"
# или по частям (если не используете DATABASE_URL)
# DB_HOST=db
# DB_PORT=5432
# DB_USER=user
# DB_PASSWORD=pass
# DB_NAME=appdb
# DB_DRIVER=postgresql+psycopg
# DB_ECHO=false

# Redis (для хранения jti токенов)
REDIS_URL="redis://redis:6379/0"
# или по частям
# REDIS_HOST=redis
# REDIS_PORT=6379
# REDIS_DB=0
# REDIS_PASSWORD=
```

Примечания:
- Убедитесь, что reverse‑proxy (например, Nginx/Traefik) корректно прокидывает заголовки и схему (`X-Forwarded-Proto=https`) при использовании `REQUIRE_HTTPS=true`.
- Значения `TOKEN_ISSUER`/`TOKEN_AUDIENCE` должны соответствовать вашим клиентам и проверяются на декодировании JWT.
- `SECRET_KEY` должен быть криптографически стойким и длиной не менее 32 символов; в `ENV != dev` приложение не стартует с дефолтным/коротким ключом.
