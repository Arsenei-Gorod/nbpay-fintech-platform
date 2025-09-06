from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import (
    UserServiceDep,
    require_current_user,
    get_token_store,
    get_refresh_store,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    ensure_token_type,
)
from app.core.config import get_settings
from app.domain.user.schemas import UserRegisterDTO, UserReadDTO, TokenDTO
from app.core.i18n import _


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserReadDTO, status_code=status.HTTP_201_CREATED
)
def register(dto: UserRegisterDTO, svc: UserServiceDep) -> UserReadDTO:
    try:
        return svc.register(dto)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenDTO)
def login(
    svc: UserServiceDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
    token_store=Depends(get_token_store),
    refresh_store=Depends(get_refresh_store),
) -> TokenDTO:
    try:
        user = svc.authenticate(form_data.username, form_data.password)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=_("invalid credentials")
        )
    settings = get_settings()
    access = create_access_token(str(user.id), extra={"role": user.role})
    refresh = create_refresh_token(str(user.id), extra={"role": user.role})
    # record access jti in token store with TTL
    token_store.allow_access(
        access["jti"], str(user.id), ttl_seconds=settings.ACCESS_TOKEN_EXPIRES_MIN * 60
    )
    # record refresh jti
    refresh_store.allow_access(
        refresh["jti"],
        str(user.id),
        ttl_seconds=settings.REFRESH_TOKEN_EXPIRES_DAYS * 86400,
    )
    return TokenDTO(access_token=access["token"], refresh_token=refresh["token"])


@router.post("/refresh", response_model=TokenDTO)
def refresh_token(
    refresh_token: str,
    svc: UserServiceDep,
    token_store=Depends(get_token_store),
    refresh_store=Depends(get_refresh_store),
) -> TokenDTO:
    try:
        payload = decode_token(refresh_token)
        ensure_token_type(payload, "refresh")
        user_id = payload.get("sub")
        jti = payload.get("jti")
        if not user_id:
            raise ValueError("invalid token payload")
        if not jti or not refresh_store.is_access_allowed(jti):
            raise ValueError("refresh revoked or unknown")
        user = svc.get(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=_("invalid refresh token")
        )
    settings = get_settings()
    # rotate tokens: revoke old refresh and issue new pair
    refresh_store.revoke_access(payload.get("jti"))  # type: ignore[arg-type]
    access = create_access_token(str(user.id), extra={"role": user.role})
    new_refresh = create_refresh_token(str(user.id), extra={"role": user.role})
    token_store.allow_access(
        access["jti"], str(user.id), ttl_seconds=settings.ACCESS_TOKEN_EXPIRES_MIN * 60
    )
    refresh_store.allow_access(
        new_refresh["jti"],
        str(user.id),
        ttl_seconds=settings.REFRESH_TOKEN_EXPIRES_DAYS * 86400,
    )
    return TokenDTO(access_token=access["token"], refresh_token=new_refresh["token"])


@router.get("/me", response_model=UserReadDTO)
def me(current: UserReadDTO = Depends(require_current_user())) -> UserReadDTO:
    return current


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_me(
    svc: UserServiceDep, current: UserReadDTO = Depends(require_current_user())
) -> Response:
    svc.delete(str(current.id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def logout(
    token: str,
    token_store=Depends(get_token_store),
    refresh_token: str | None = None,
    refresh_store=Depends(get_refresh_store),
) -> Response:
    # Best-effort revoke access token by jti
    try:
        payload = decode_token(token)
        ensure_token_type(payload, "access")
        jti = payload.get("jti")
        if jti:
            token_store.revoke_access(jti)
    except Exception:
        pass
    # Optional refresh revoke
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            ensure_token_type(payload, "refresh")
            jti = payload.get("jti")
            if jti:
                refresh_store.revoke_access(jti)
        except Exception:
            pass
    return Response(status_code=status.HTTP_204_NO_CONTENT)
