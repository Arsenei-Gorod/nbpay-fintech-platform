from __future__ import annotations

import pytest

from app.domain.user.services import UserService
from app.infrastructure.repositories.user_inmemory import InMemoryUserRepository
from app.infrastructure.cache.password_reset_store import InMemoryPasswordResetStore


@pytest.fixture()
def repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture()
def reset_store() -> InMemoryPasswordResetStore:
    return InMemoryPasswordResetStore()


@pytest.fixture()
def service(
    repo: InMemoryUserRepository, reset_store: InMemoryPasswordResetStore
) -> UserService:
    return UserService(user_repo=repo, password_reset_store=reset_store)
