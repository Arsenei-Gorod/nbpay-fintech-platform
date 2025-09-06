# Repository Guidelines

## Project Structure & Module Organization
- Source lives under `app/` with layers: `core/` (settings, logging), `api/` (routers, dependencies), `domain/` (entities, schemas, repositories, services), `infrastructure/` (adapters), and `main.py` (app factory).
- Example paths: `app/api/v1/routers/users.py`, `app/domain/user/services.py`, `app/infrastructure/repositories/user_inmemory.py`.
- Keep boundaries clean: API calls services; services depend on repository interfaces; infrastructure implements those interfaces.

## Build, Test, and Development Commands
- Setup: `uv venv` then `uv sync` to create venv and install deps.
- Run (dev, hot reload): `uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000`.
- Run (uvicorn): `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.
- Tests: `uv run pytest -q`.
- Lint: `uv run ruff check .`  |  Format: `uv run ruff format .`.

## Coding Style & Naming Conventions
- Python 3.11+, 4‑space indentation, type hints required for public APIs.
- Modules and functions: `snake_case`; classes and schemas: `PascalCase`; constants: `UPPER_SNAKE_CASE`.
- Prefer pure domain logic in `domain/`; avoid framework imports there. Validation via Pydantic DTOs in `schemas.py`.
- Use structured logging via `structlog` (see `app/core/logging.py`).

## Testing Guidelines
- Framework: `pytest`; add tests under `tests/` mirroring `app/` (e.g., `tests/api/test_users.py`).
- Naming: files `test_*.py`; tests `def test_*`.
- FastAPI example: use `httpx.AsyncClient` against `app.create_app()` for endpoint tests.
- Aim for meaningful coverage of services and routers; no strict threshold enforced.

## Commit & Pull Request Guidelines
- Commits: concise imperative subject; optionally follow Conventional Commits (e.g., `feat(api): add users router`).
- PRs: include description, rationale, screenshots for API docs if UI‑affecting, and linked issues. Note breaking changes.
- Ensure CI‑green locally: lint and tests pass before requesting review.

## Security & Configuration Tips
- Configuration is in `app/core/config.py` via environment variables (`.env`, `.env.local`). Do not commit secrets.
- Toggle docs with `ENABLE_DOCS`; set `API_PREFIX` if serving behind a proxy.
- Commit `uv.lock` when dependencies change for reproducible installs.
