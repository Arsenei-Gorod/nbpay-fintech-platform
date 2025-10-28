from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field
from app.domain.user.models import Role


class UserCreateDTO(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2)


class UserUpdateDTO(BaseModel):
    full_name: str = Field(min_length=2)
    is_active: bool | None = None


class UserReadDTO(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool
    role: Role = Role.USER
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class UserRegisterDTO(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2)
    password: str = Field(min_length=6)


class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str


class TokenDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
