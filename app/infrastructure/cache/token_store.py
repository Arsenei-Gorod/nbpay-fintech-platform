from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol, Any


class TokenStore(Protocol):
    def allow_access(self, jti: str, user_id: str, ttl_seconds: int) -> None: ...
    def is_access_allowed(self, jti: str) -> bool: ...
    def revoke_access(self, jti: str) -> None: ...


@dataclass
class _Entry:
    user_id: str
    expires_at: float


class InMemoryTokenStore(TokenStore):
    """Simple in-memory token store with TTL suitable for tests/dev."""

    def __init__(self) -> None:
        self._data: dict[str, _Entry] = {}

    def _gc(self) -> None:
        now = time.time()
        for k in list(self._data.keys()):
            if self._data[k].expires_at <= now:
                self._data.pop(k, None)

    def allow_access(self, jti: str, user_id: str, ttl_seconds: int) -> None:
        self._gc()
        self._data[jti] = _Entry(user_id=user_id, expires_at=time.time() + ttl_seconds)

    def is_access_allowed(self, jti: str) -> bool:
        self._gc()
        return jti in self._data

    def revoke_access(self, jti: str) -> None:
        self._data.pop(jti, None)


class RedisTokenStore(TokenStore):
    """Redis-backed token store.

    Requires `redis` package and a running Redis server. This class is optional
    and not used in tests unless REDIS_URL is configured.
    """

    def __init__(self, redis_client: Any, namespace: str = "auth:access") -> None:
        self.r = redis_client
        self.ns = namespace

    def _key(self, jti: str) -> str:
        return f"{self.ns}:{jti}"

    def allow_access(self, jti: str, user_id: str, ttl_seconds: int) -> None:
        self.r.set(self._key(jti), user_id, ex=ttl_seconds)

    def is_access_allowed(self, jti: str) -> bool:
        return self.r.exists(self._key(jti)) == 1

    def revoke_access(self, jti: str) -> None:
        self.r.delete(self._key(jti))
