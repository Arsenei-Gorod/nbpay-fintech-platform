from fastapi import APIRouter, Response, status, Depends

from app.api.dependencies import UserServiceDep, require_roles
from app.domain.user.models import Role
from app.domain.user.schemas import (
    UserCreateDTO,
    UserReadDTO,
    UserUpdateDTO,
)
from app.utils.exceptions import to_http


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserReadDTO, status_code=status.HTTP_201_CREATED)
def create_user(
    dto: UserCreateDTO,
    svc: UserServiceDep,
    _: object = Depends(require_roles(Role.ADMIN)),
) -> UserReadDTO:
    try:
        return svc.create(dto)
    except Exception as e:  # map domain/app errors to HTTP
        raise to_http(e)


@router.get("/{user_id}", response_model=UserReadDTO)
def read_user(
    user_id: str, svc: UserServiceDep, _: object = Depends(require_roles(Role.ADMIN))
) -> UserReadDTO:
    try:
        return svc.get(user_id)
    except Exception as e:
        raise to_http(e)


@router.patch("/{user_id}", response_model=UserReadDTO)
def update_user(
    user_id: str,
    dto: UserUpdateDTO,
    svc: UserServiceDep,
    _: object = Depends(require_roles(Role.ADMIN)),
) -> UserReadDTO:
    try:
        return svc.update(user_id, dto)
    except Exception as e:
        raise to_http(e)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str, svc: UserServiceDep, _: object = Depends(require_roles(Role.ADMIN))
) -> Response:
    try:
        svc.delete(user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise to_http(e)


@router.post("/{user_id}/grant-admin", response_model=UserReadDTO)
def grant_admin(
    user_id: str, svc: UserServiceDep, _: object = Depends(require_roles(Role.ADMIN))
) -> UserReadDTO:
    try:
        return svc.set_role(user_id, Role.ADMIN)
    except Exception as e:
        raise to_http(e)
