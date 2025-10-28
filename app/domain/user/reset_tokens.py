from __future__ import annotations

from typing import Protocol


class PasswordResetStore(Protocol):
    """Interface for issuing and consuming password reset tokens."""

    def issue(self, user_id: str, ttl_seconds: int) -> str: ...

    def consume(self, token: str) -> str | None: ...

    def peek(self, token: str) -> str | None: ...
