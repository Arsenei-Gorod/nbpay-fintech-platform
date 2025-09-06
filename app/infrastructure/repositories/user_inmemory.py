from __future__ import annotations

from dataclasses import replace
from typing import Dict
from uuid import UUID

from app.domain.user.models import User
from app.domain.user.repositories import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._store: Dict[UUID, User] = {}

    def add(self, user: User) -> User:
        self._store[user.id] = replace(user)
        return replace(self._store[user.id])

    def get(self, user_id: UUID) -> User | None:
        u = self._store.get(user_id)
        return replace(u) if u else None

    def get_by_email(self, email: str) -> User | None:
        for u in self._store.values():
            if u.email == email:
                return replace(u)
        return None

    def update(self, user: User) -> User:
        if user.id not in self._store:
            raise KeyError("user not found")
        self._store[user.id] = replace(user)
        return replace(self._store[user.id])

    def delete(self, user_id: UUID) -> None:
        self._store.pop(user_id, None)
