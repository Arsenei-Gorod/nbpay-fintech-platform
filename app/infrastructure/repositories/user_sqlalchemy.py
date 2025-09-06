from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.domain.user.models import User, Role
from app.domain.user.repositories import UserRepository
from app.infrastructure.models.user import UserORM


class SQLUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_domain(self, orm: UserORM) -> User:
        return User(
            id=UUID(str(orm.id)),
            email=orm.email,
            full_name=orm.full_name,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            password_hash=getattr(orm, "password_hash", ""),
            role=Role(orm.role) if getattr(orm, "role", None) else Role.USER,
        )

    def _to_orm(self, user: User) -> UserORM:
        return UserORM(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            password_hash=getattr(user, "password_hash", ""),
            role=user.role.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def add(self, user: User) -> User:
        orm = self._to_orm(user)
        self.session.add(orm)
        self.session.flush()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def get(self, user_id: UUID) -> Optional[User]:
        stmt = select(UserORM).where(UserORM.id == str(user_id))
        orm = self.session.scalar(stmt)
        return self._to_domain(orm) if orm else None

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserORM).where(UserORM.email == email)
        orm = self.session.scalar(stmt)
        return self._to_domain(orm) if orm else None

    def update(self, user: User) -> User:
        # fetch existing and update fields
        stmt = select(UserORM).where(UserORM.id == str(user.id))
        orm = self.session.scalar(stmt)
        if not orm:
            raise KeyError("user not found")
        orm.email = user.email
        orm.full_name = user.full_name
        orm.is_active = user.is_active
        orm.password_hash = getattr(user, "password_hash", orm.password_hash)
        orm.role = user.role.value
        orm.updated_at = datetime.utcnow()
        self.session.add(orm)
        self.session.flush()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def delete(self, user_id: UUID) -> None:
        stmt = delete(UserORM).where(UserORM.id == str(user_id))
        self.session.execute(stmt)
