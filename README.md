# nbpay-fintech-platform  (Clean Architecture) + UV

Полноценный скелет авторизации на FastAPI: чистая архитектура, JWT access/refresh, роли, i18n, dev‑фронтенд на React + MUI и инструменты для локальной разработки. Управление зависимостями и запуск через UV (Astral).

## Layers
- Domain: Entities and repository interfaces (pure business rules).
- Application (Services): Use-cases orchestrating domain logic.
- Infrastructure: Implementations of interfaces (e.g., repositories), adapters to external systems.
- API (Presentation): HTTP routers/controllers, DTOs and dependency wiring.
- Core: Settings, logging and cross-cutting concerns.

## Structure
```
app/
  api/
    v1/
      routers/
        users.py
    dependencies.py
  core/
    config.py
    logging.py
  domain/
    user/
      models.py
      repositories.py
      schemas.py
      services.py
  infrastructure/
    repositories/
      user_inmemory.py
  main.py
```

## Prerequisites
- Python 3.11+
- UV (Astral) installed: https://docs.astral.sh/uv/

## Setup
```bash
# 1) Create a virtualenv and install deps
uv venv
uv sync

# 2) Copy and adjust environment variables
cp .env.example .env
```

## Run (development)
```bash
# Using FastAPI's dev server (hot reload)
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000

# Or via Uvicorn directly
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open docs at http://localhost:8000/docs

## PostgreSQL (Docker)
```bash
# Start PostgreSQL locally
docker compose up -d db

# Configure environment (see .env.example)
cp .env.example .env

# Run the app (uses DATABASE_URL from .env)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Root endpoint returns a greeting at `/`.

## Frontend microservice (React + MUI)

- Source at `frontend/` (React 18 + Vite + React Router + MUI).
- Dev start locally:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. API calls are proxied to the backend at http://localhost:8000 (see `frontend/.env.development`).

- Or via Docker:

```bash
docker compose up -d frontend
```

This exposes http://localhost:5173 and proxies API to `host.docker.internal:8000`.

## Dev vs Prod environments

Профили Docker Compose разделяют базовые сервисы и dev‑инструменты.

- Базовые: `db`, `redis`
- Dev‑только: `backend`, `frontend`, `cloudbeaver`

Команды:

```bash
# База (БД + Redis)
docker compose up -d db redis

# Полный dev стек
docker compose --profile dev up -d --build

# Остановить только dev
docker compose --profile dev stop

# Остановить всё
docker compose down
```

CloudBeaver (DBeaver Web): http://localhost:8978 (admin/admin)
- Host: db, Port: 5432, DB: appdb, User: postgres, Pass: postgres

## i18n

- `LANG` — язык сервера (`en` или `ru`).
- Переводы: `app/locales/<lang>/LC_MESSAGES/messages.po` (gettext). Компиляция `.mo`:

```bash
msgfmt -o app/locales/ru/LC_MESSAGES/messages.mo app/locales/ru/LC_MESSAGES/messages.po
```

## Documentation

Документация лежит в `docs/` и собирается MkDocs (через UV).

```bash
uv run mkdocs serve -a 0.0.0.0:8001   # live-docs
uv run mkdocs build                    # build to site/
```

Разделы:
- Введение: структура, возможности
- Быстрый старт: запуск, переменные окружения
- Авторизация: схемы и эндпоинты


## Dev vs Prod environments

This repo uses Docker Compose profiles to separate dev tooling/services from the baseline stack.

- Default services: `db`, `redis` (no profile — run in any environment)
- Dev-only services: `backend`, `frontend`, `cloudbeaver` (profile `dev`)

Commands:

```bash
# Start DB + Redis (baseline)
docker compose up -d db redis

# Start full dev stack (adds backend + frontend + CloudBeaver)
docker compose --profile dev up -d

# Stop only dev services
docker compose --profile dev stop

# Stop everything
docker compose down
```

CloudBeaver (DBeaver Web) runs at http://localhost:8978 (dev profile). On first open, log in with:

- Username: `admin`
- Password: `admin`

Add a PostgreSQL connection with:

- Host: `db`
- Port: `5432`
- Database: `appdb`
- User: `postgres`
- Password: `postgres`

These values match the `db` service configuration in `docker-compose.yml`.

Backend (dev) runs at http://localhost:8000 with auto-reload using `fastapi dev` inside the container and is reachable as `http://backend:8000` from other dev services.

## Internationalization (i18n)

- Configure language via env var `LANG` (default `en`). Example: `LANG=ru`.
- Translations use GNU gettext with domain `messages` and locales under `app/locales/<lang>/LC_MESSAGES/messages.po`.
- Current keys covered: `invalid credentials`, `invalid token`, `invalid refresh token`, `insufficient privileges`, `HTTPS required`.
- Add or update translations:

```
# Edit PO files
app/locales/ru/LC_MESSAGES/messages.po
app/locales/en/LC_MESSAGES/messages.po

# Compile to .mo (requires gettext utilities installed on host)
msgfmt -o app/locales/ru/LC_MESSAGES/messages.mo app/locales/ru/LC_MESSAGES/messages.po
msgfmt -o app/locales/en/LC_MESSAGES/messages.mo app/locales/en/LC_MESSAGES/messages.po

# Restart backend to pick them up
docker compose --profile dev restart backend
```

- If `.mo` files are missing, the backend falls back to built-in minimal Russian translations for the keys above and returns English by default for the rest.

## Notes
- Repository wiring is in `app/api/dependencies.py`. Swap `InMemoryUserRepository` for a DB-backed repo later without touching the service/API layers.
- `app/domain/user/services.py` holds business logic.
- `app/domain/user/models.py` is a domain entity (dataclass) with domain behavior.
- `app/domain/user/schemas.py` are DTOs for request/response.
- Add real DB by implementing `UserRepository` in infrastructure and providing it in dependencies.

## Testing
```bash
uv run pytest -q
```

## Security

- SECRET_KEY: set a strong random value (>= 32 chars) in non-dev; the app refuses to start in non-dev if the key is weak/default.
- HTTPS: enable `REQUIRE_HTTPS=true` in production to reject plain HTTP requests.
- JWT claims: access/refresh tokens include `jti`, `iat`, `nbf`, `exp` (+ `iss`/`aud` if configured). Validation requires `exp`, `iat`, `nbf` and verifies `iss`/`aud` when set.
- Role claims: by default `TRUST_TOKEN_ROLE=true` allows role claims in tokens to gate admin endpoints. For maximum safety, set `TRUST_TOKEN_ROLE=false` to rely only on the role from the database.

## Frontend auth integration

- The dev frontend in `frontend/` stores `access_token`/`refresh_token` in `localStorage` and injects `Authorization: Bearer <access>` on requests.
- On 401, it attempts to refresh via `POST /api/v1/auth/refresh?refresh_token=...` and retries the original request. The interceptor avoids looping on `/auth/login` and `/auth/refresh`.
- Logout calls `POST /api/v1/auth/logout` with both tokens so the backend can revoke them; the client then clears local storage and redirects to `/login`.

Recommended prod hardening: set `REQUIRE_HTTPS=true` and `TRUST_TOKEN_ROLE=false`, and prefer HTTP-only secure cookies over localStorage if you later add a server-side session facade.

## Management commands

Create a superuser (requires `DATABASE_URL` configured):

```bash
uv run python -m app.cli.manage create-superuser \
  --email admin@example.com \
  --full-name "Admin User"
# You will be prompted for a password (or pass --password "...")
```

Use `--upgrade-if-exists` to promote an existing account to admin:

```bash
uv run python -m app.cli.manage create-superuser \
  --email admin@example.com \
  --full-name "Admin User" \
  --upgrade-if-exists
```
