from __future__ import annotations

from uuid import UUID

import structlog

from app.domain.user.models import User, Role
from app.domain.user.repositories import UserRepository
from app.domain.user.schemas import (
    UserCreateDTO,
    UserReadDTO,
    UserUpdateDTO,
    UserRegisterDTO,
)
from app.utils.exceptions import NotFoundError
from app.core.security import get_password_hash, verify_password


logger = structlog.get_logger()


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._users = user_repo

    def create(self, dto: UserCreateDTO) -> UserReadDTO:
        if self._users.get_by_email(dto.email):
            raise ValueError("email already in use")
        user = User(email=str(dto.email), full_name=dto.full_name)
        user = self._users.add(user)
        logger.info("user.created", user_id=str(user.id), email=user.email)
        return UserReadDTO.model_validate(user)

    def get(self, user_id: str) -> UserReadDTO:
        user = self._users.get(UUID(user_id))
        if not user:
            raise NotFoundError("user not found")
        return UserReadDTO.model_validate(user)

    def update(self, user_id: str, dto: UserUpdateDTO) -> UserReadDTO:
        user = self._users.get(UUID(user_id))
        if not user:
            raise NotFoundError("user not found")
        if dto.full_name:
            user.rename(dto.full_name)
        if dto.is_active is not None:
            user.is_active = dto.is_active
        user = self._users.update(user)
        logger.info("user.updated", user_id=str(user.id))
        return UserReadDTO.model_validate(user)

    def delete(self, user_id: str) -> None:
        self._users.delete(UUID(user_id))
        logger.info("user.deleted", user_id=user_id)

    # Auth flows
    def register(self, dto: UserRegisterDTO) -> UserReadDTO:
        if self._users.get_by_email(dto.email):
            raise ValueError("email already in use")
        user = User(
            email=str(dto.email),
            full_name=dto.full_name,
            password_hash=get_password_hash(dto.password),
        )
        user = self._users.add(user)
        logger.info("auth.registered", user_id=str(user.id))
        return UserReadDTO.model_validate(user)

    def authenticate(self, email: str, password: str) -> UserReadDTO:
        user = self._users.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("invalid credentials")
        if not user.is_active:
            raise ValueError("inactive user")
        return UserReadDTO.model_validate(user)

    def set_role(self, user_id: str, role: Role) -> UserReadDTO:
        user = self._users.get(UUID(user_id))
        if not user:
            raise NotFoundError("user not found")
        user.role = role
        user = self._users.update(user)
        logger.info("user.role_updated", user_id=str(user.id), role=user.role)
        return UserReadDTO.model_validate(user)
