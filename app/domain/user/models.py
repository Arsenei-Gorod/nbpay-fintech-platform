from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"


@dataclass(slots=True)
class User:
    id: UUID = field(default_factory=uuid4)
    email: str = ""
    full_name: str = ""
    is_active: bool = True
    password_hash: str = ""
    role: Role = Role.USER
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def rename(self, full_name: str) -> None:
        if not full_name or len(full_name) < 2:
            raise ValueError("full_name is too short")
        self.full_name = full_name
        self.updated_at = datetime.utcnow()
