from __future__ import annotations

import pytest

from app.domain.user.services import UserService
from app.infrastructure.repositories.user_inmemory import InMemoryUserRepository


@pytest.fixture()
def repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture()
def service(repo: InMemoryUserRepository) -> UserService:
    return UserService(user_repo=repo)
