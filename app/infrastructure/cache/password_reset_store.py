from __future__ import annotations

import secrets
import time
from dataclasses import dataclass
from typing import Any

from app.domain.user.reset_tokens import PasswordResetStore


@dataclass
class _Entry:
    user_id: str
    expires_at: float


class InMemoryPasswordResetStore(PasswordResetStore):
    """Simple in-memory store for password reset tokens."""

    def __init__(self) -> None:
        self._tokens: dict[str, _Entry] = {}

    def _gc(self) -> None:
        now = time.time()
        for token in list(self._tokens.keys()):
            entry = self._tokens.get(token)
            if entry and entry.expires_at <= now:
                self._tokens.pop(token, None)

    def issue(self, user_id: str, ttl_seconds: int) -> str:
        self._gc()
        token = secrets.token_urlsafe(32)
        self._tokens[token] = _Entry(user_id=user_id, expires_at=time.time() + ttl_seconds)
        return token

    def consume(self, token: str) -> str | None:
        self._gc()
        entry = self._tokens.pop(token, None)
        if not entry:
            return None
        if entry.expires_at <= time.time():
            return None
        return entry.user_id

    def peek(self, token: str) -> str | None:
        self._gc()
        entry = self._tokens.get(token)
        if not entry:
            return None
        if entry.expires_at <= time.time():
            self._tokens.pop(token, None)
            return None
        return entry.user_id


class RedisPasswordResetStore(PasswordResetStore):
    """Redis-backed password reset token store."""

    def __init__(self, redis_client: Any, namespace: str = "auth:reset") -> None:
        self._redis = redis_client
        self._namespace = namespace

    def _key(self, token: str) -> str:
        return f"{self._namespace}:{token}"

    def issue(self, user_id: str, ttl_seconds: int) -> str:
        token = secrets.token_urlsafe(32)
        self._redis.set(self._key(token), user_id, ex=ttl_seconds)
        return token

    def consume(self, token: str) -> str | None:
        key = self._key(token)
        pipe = self._redis.pipeline()
        pipe.get(key)
        pipe.delete(key)
        value, _ = pipe.execute()
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)

    def peek(self, token: str) -> str | None:
        value = self._redis.get(self._key(token))
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)
