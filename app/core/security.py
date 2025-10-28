from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _base_claims(
    subject: str, token_type: Literal["access", "refresh"]
) -> dict[str, Any]:
    settings = get_settings()
    claims: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "jti": str(uuid4()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    # Bind not-before to issued-at to prevent early use
    claims["nbf"] = claims["iat"]
    if settings.TOKEN_ISSUER:
        claims["iss"] = settings.TOKEN_ISSUER
    if settings.TOKEN_AUDIENCE:
        claims["aud"] = settings.TOKEN_AUDIENCE
    return claims


def create_access_token(
    subject: str, *, minutes: int | None = None, extra: dict[str, Any] | None = None
) -> dict[str, str]:
    settings = get_settings()
    exp_minutes = minutes if minutes is not None else settings.ACCESS_TOKEN_EXPIRES_MIN
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)
    claims = _base_claims(subject, "access")
    claims["exp"] = expire
    if extra:
        claims.update(extra)
    token = jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return {"token": token, "jti": claims["jti"]}


def create_refresh_token(
    subject: str, *, days: int | None = None, extra: dict[str, Any] | None = None
) -> dict[str, str]:
    settings = get_settings()
    exp_days = days if days is not None else settings.REFRESH_TOKEN_EXPIRES_DAYS
    expire = datetime.now(timezone.utc) + timedelta(days=exp_days)
    claims = _base_claims(subject, "refresh")
    claims["exp"] = expire
    if extra:
        claims.update(extra)
    token = jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return {"token": token, "jti": claims["jti"]}


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "require_exp": True,
                "require_iat": True,
                "require_nbf": True,
                "verify_aud": bool(settings.TOKEN_AUDIENCE),
            },
            audience=settings.TOKEN_AUDIENCE,
            issuer=settings.TOKEN_ISSUER,
        )
        return payload
    except JWTError as e:
        raise ValueError("invalid token") from e


def ensure_token_type(
    payload: dict[str, Any], expected: Literal["access", "refresh"]
) -> None:
    t = payload.get("type")
    if t != expected:
        raise ValueError("invalid token type")
