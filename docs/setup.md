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
- `LANG` — язык сообщений (`en` или `ru`)
- `API_PREFIX` — префикс API (по умолчанию `/api`)
- `SECRET_KEY` — секрет для JWT
- `DATABASE_URL` или `DB_*` параметры для БД
- `REDIS_URL` или `REDIS_*` параметры для Redis

См. `.env.example` для полного списка.

## Сборка документации
```
uv run mkdocs serve -a 0.0.0.0:8001   # dev-сервер доков
# или
uv run mkdocs build                    # сборка в каталог site/
```

