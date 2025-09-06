from __future__ import annotations

from time import sleep
from uuid import uuid4

import pytest

from app.core.security import verify_password
from app.domain.user.schemas import (
    UserCreateDTO,
    UserRegisterDTO,
    UserUpdateDTO,
)
from app.utils.exceptions import NotFoundError


def test_create_user_success(service) -> None:
    dto = UserCreateDTO(email="alice@example.com", full_name="Alice")
    out = service.create(dto)
    assert out.email == dto.email
    assert out.full_name == dto.full_name
    assert out.is_active is True
    # password_hash should never be present in read DTO
    assert "password_hash" not in out.model_dump()


def test_create_user_duplicate_email(service) -> None:
    dto = UserCreateDTO(email="dup@example.com", full_name="First")
    service.create(dto)
    with pytest.raises(ValueError):
        service.create(UserCreateDTO(email="dup@example.com", full_name="Second"))


def test_get_user_success(service) -> None:
    created = service.create(UserCreateDTO(email="bob@example.com", full_name="Bob"))
    out = service.get(str(created.id))
    assert out.id == created.id
    assert out.email == "bob@example.com"


def test_get_user_not_found_raises(service) -> None:
    with pytest.raises(NotFoundError):
        service.get(str(uuid4()))


def test_get_user_invalid_uuid_raises(service) -> None:
    with pytest.raises(ValueError):
        service.get("not-a-uuid")


def test_update_user_full_name_and_active(service, repo) -> None:
    created = service.create(
        UserCreateDTO(email="carol@example.com", full_name="Carol")
    )
    before = service.get(str(created.id))

    # ensure updated_at changes; sleep(0) unreliable, add tiny delay if needed
    sleep(0.001)
    out = service.update(
        str(created.id),
        UserUpdateDTO(full_name="Carolyn", is_active=False),
    )
    assert out.full_name == "Carolyn"
    assert out.is_active is False
    assert out.updated_at > before.updated_at

    # is_active None should keep prior state
    again = service.update(
        str(created.id), UserUpdateDTO(full_name="Car O.", is_active=None)
    )
    assert again.is_active is False
    assert again.full_name == "Car O."


def test_update_user_not_found_raises(service) -> None:
    with pytest.raises(NotFoundError):
        # Use a valid full_name (min_length=2) so validation doesn't mask NotFoundError
        service.update(str(uuid4()), UserUpdateDTO(full_name="XX", is_active=True))


def test_update_user_invalid_uuid_raises(service) -> None:
    with pytest.raises(ValueError):
        service.update("bad-uuid", UserUpdateDTO(full_name="Name", is_active=True))


def test_delete_user_ok_even_if_missing(service) -> None:
    # deleting missing should not raise by design (repo pop ignores missing)
    service.delete(str(uuid4()))


def test_delete_user_invalid_uuid_raises(service) -> None:
    with pytest.raises(ValueError):
        service.delete("bad-uuid")


def test_register_hashes_password_and_hides_sensitive(service, repo) -> None:
    reg = service.register(
        UserRegisterDTO(
            email="dave@example.com", full_name="Dave", password="secret123"
        )
    )
    assert reg.email == "dave@example.com"
    # Ensure storage contains a hashed password, not plaintext
    stored = repo.get(reg.id)
    assert stored is not None
    assert stored.password_hash and stored.password_hash != "secret123"
    assert verify_password("secret123", stored.password_hash)
    # DTO must not leak password_hash
    assert "password_hash" not in reg.model_dump()


def test_register_duplicate_email_raises(service) -> None:
    service.register(
        UserRegisterDTO(email="eve@example.com", full_name="Eve", password="hunter2")
    )
    with pytest.raises(ValueError):
        service.register(
            UserRegisterDTO(
                email="eve@example.com", full_name="Eve 2", password="newpass"
            )
        )


def test_authenticate_success(service) -> None:
    user = service.register(
        UserRegisterDTO(
            email="frank@example.com", full_name="Frank", password="p@ssw0rd"
        )
    )
    authed = service.authenticate("frank@example.com", "p@ssw0rd")
    assert authed.id == user.id


def test_authenticate_invalid_password_raises(service) -> None:
    service.register(
        UserRegisterDTO(email="gina@example.com", full_name="Gina", password="correct")
    )
    with pytest.raises(ValueError):
        service.authenticate("gina@example.com", "wrong")


def test_authenticate_invalid_email_raises(service) -> None:
    with pytest.raises(ValueError):
        service.authenticate("nobody@example.com", "anything")


def test_authenticate_inactive_user_raises(service, repo) -> None:
    reg = service.register(
        UserRegisterDTO(
            email="harry@example.com", full_name="Harry", password="passw0rd"
        )
    )
    # toggle to inactive
    service.update(str(reg.id), UserUpdateDTO(full_name="Harry", is_active=False))
    with pytest.raises(ValueError):
        service.authenticate("harry@example.com", "passw0rd")
