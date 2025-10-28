from typing import Annotated, Generator, Callable

from fastapi import Depends, HTTPException, status

from app.core.config import get_settings
from app.domain.user.services import UserService
from app.domain.user.schemas import UserReadDTO
from app.domain.user.models import Role
from app.infrastructure.repositories.user_inmemory import InMemoryUserRepository
from app.infrastructure.repositories.user_sqlalchemy import (
    SQLUserRepository,
)
from app.infrastructure.db.session import get_session
from app.infrastructure.cache.token_store import InMemoryTokenStore, RedisTokenStore
from app.core.security import decode_token
from app.core.i18n import _


_MEM_REPO: InMemoryUserRepository | None = None


def get_user_service() -> Generator[UserService, None, None]:
    """Provide a UserService wired to either SQL repo (if DATABASE_URL set) or a shared in-memory repo.

    For in-memory mode, use a module-level singleton so state persists across requests within a process,
    which is necessary for tests that register then authenticate.
    """
    settings = get_settings()
    if settings.DATABASE_URL:
        with get_session() as session:
            repo = SQLUserRepository(session)
            yield UserService(user_repo=repo)
    else:
        global _MEM_REPO
        if _MEM_REPO is None:
            _MEM_REPO = InMemoryUserRepository()
        yield UserService(user_repo=_MEM_REPO)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


# Token store provider (in-memory by default; Redis if configured)
_TOKEN_STORE: InMemoryTokenStore | None = None
_REFRESH_STORE: InMemoryTokenStore | None = None


def get_token_store():
    settings = get_settings()
    if settings.REDIS_URL:
        try:
            import redis  # type: ignore

            client = redis.Redis.from_url(settings.REDIS_URL)
            return RedisTokenStore(client)
        except Exception:  # pragma: no cover - optional
            # fallback silently to in-memory if redis not available
            pass
    global _TOKEN_STORE
    if _TOKEN_STORE is None:
        _TOKEN_STORE = InMemoryTokenStore()
    return _TOKEN_STORE


def get_refresh_store():
    settings = get_settings()
    if settings.REDIS_URL:
        try:
            import redis  # type: ignore

            client = redis.Redis.from_url(settings.REDIS_URL)
            return RedisTokenStore(client, namespace="auth:refresh")
        except Exception:  # pragma: no cover
            pass
    global _REFRESH_STORE
    if _REFRESH_STORE is None:
        _REFRESH_STORE = InMemoryTokenStore()
    return _REFRESH_STORE


def get_current_user(
    svc: UserServiceDep, token_store=Depends(get_token_store)
) -> UserReadDTO:
    # Placeholder kept for backwards-compatibility; use require_current_user() instead
    from fastapi.security import OAuth2PasswordBearer

    _ = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
    raise RuntimeError("This dependency must be used via require_current_user() helper")


def require_current_user() -> Callable[[UserService], UserReadDTO]:
    from fastapi.security import OAuth2PasswordBearer

    oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

    def dep(
        svc: UserService = Depends(get_user_service),
        token: str = Depends(oauth2),
        token_store=Depends(get_token_store),
    ) -> UserReadDTO:  # type: ignore[return-type]
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                raise ValueError("invalid token type")
            jti = payload.get("jti")
            if not jti or not token_store.is_access_allowed(jti):
                raise ValueError("token revoked or unknown")
            sub = payload.get("sub")
            if not sub:
                raise ValueError("invalid token payload")
            user = svc.get(sub)
            return user
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=_("invalid token")
            )

    return dep


def require_roles(*roles: Role) -> Callable[[UserReadDTO], UserReadDTO]:
    from fastapi.security import OAuth2PasswordBearer

    oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

    def dep(
        current: UserReadDTO = Depends(require_current_user()),
        token: str = Depends(oauth2),
    ) -> UserReadDTO:
        settings = get_settings()
        effective_role = Role(current.role)  # type: ignore[arg-type]
        if settings.TRUST_TOKEN_ROLE:
            try:
                payload = decode_token(token)
                claim_role = payload.get("role")
                effective_role = Role(claim_role) if claim_role else effective_role  # type: ignore[arg-type]
            except Exception:
                pass
        if roles and effective_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=_("insufficient privileges")
            )
        return current

    return dep
