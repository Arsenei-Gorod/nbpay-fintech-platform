# FastAPI Auth Skeleton

Минимальный, но полноценный скелет авторизации на FastAPI с чистой архитектурой, JWT access/refresh, ролями и i18n. Подходит как база для своих проектов.

- Бэкенд: FastAPI + чистая архитектура (`app/`)
- Хранилище: PostgreSQL (или InMemory), Redis (для хранения `jti` токенов) — опционально
- Фронтенд (dev): React + MUI (микросервис `frontend/`) — опционально
- DBeaver Web: CloudBeaver (dev), для просмотра БД
- Сборка и управление: UV (Astral), Docker Compose

## Возможности
- Регистрация, вход (`OAuth2PasswordRequestForm`), обновление токена, профиль, выход
- Разделение access/refresh, ротация refresh, отзыв по `jti` через Redis/InMemory
- Роли и защита эндпоинтов
- i18n через gettext (RU/EN), выбор языка через `LANG`
- Разделение dev/prod сервисов через Compose profiles

См. раздел «Быстрый старт» для запуска и «Авторизация» для деталей API.

