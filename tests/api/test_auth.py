import pytest
from httpx import AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_register_login_me_delete() -> None:
    app = create_app()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Register
        payload = {
            "email": "user@example.com",
            "full_name": "Test User",
            "password": "secret123",
        }
        r = await ac.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == payload["email"]

        # Login
        form = {"username": payload["email"], "password": payload["password"]}
        r = await ac.post("/api/v1/auth/login", data=form)
        assert r.status_code == 200
        tokens = r.json()
        assert "access_token" in tokens and "refresh_token" in tokens
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Me
        r = await ac.get("/api/v1/auth/me", headers=headers)
        assert r.status_code == 200
        me = r.json()
        assert me["email"] == payload["email"]

        # Refresh
        r = await ac.post(
            "/api/v1/auth/refresh", params={"refresh_token": refresh_token}
        )
        assert r.status_code == 200
        refreshed = r.json()
        assert "access_token" in refreshed and "refresh_token" in refreshed
        new_access = refreshed["access_token"]
        headers = {"Authorization": f"Bearer {new_access}"}

        # Delete self
        r = await ac.delete("/api/v1/auth/me", headers=headers)
        assert r.status_code == 204

        # Access after delete should be unauthorized or not found
        r = await ac.get("/api/v1/auth/me", headers=headers)
        assert r.status_code in (401, 404)


@pytest.mark.asyncio
async def test_logout_revokes_access() -> None:
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "email": "logout@example.com",
            "full_name": "Lo Gout",
            "password": "secret123",
        }
        r = await ac.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 201
        r = await ac.post(
            "/api/v1/auth/login",
            data={"username": payload["email"], "password": payload["password"]},
        )
        assert r.status_code == 200
        tokens = r.json()
        access = tokens["access_token"]

        # Verify works
        r = await ac.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"}
        )
        assert r.status_code == 200

        # Logout (revoke access)
        r = await ac.post("/api/v1/auth/logout", params={"token": access})
        assert r.status_code == 204

        # Access should now be invalid
        r = await ac.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"}
        )
        assert r.status_code == 401


@pytest.mark.asyncio
async def test_admin_required_for_user_routes() -> None:
    # Create normal user and ensure access to admin endpoints is forbidden
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "email": "u1@example.com",
            "full_name": "U One",
            "password": "secret123",
        }
        r = await ac.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 201
        # login as normal user
        r = await ac.post(
            "/api/v1/auth/login",
            data={"username": payload["email"], "password": payload["password"]},
        )
        tokens = r.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # try to create a user (admin-only)
        r = await ac.post(
            "/api/v1/users",
            headers=headers,
            json={"email": "x@example.com", "full_name": "X"},
        )
        assert r.status_code == 403


@pytest.mark.asyncio
async def test_admin_token_can_access_user_routes() -> None:
    from app.core.security import create_access_token
    from app.api.dependencies import get_token_store

    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Register a base user (we will impersonate as admin via token claims)
        payload = {
            "email": "adminlike@example.com",
            "full_name": "Admin Like",
            "password": "secret123",
        }
        r = await ac.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 201
        user_id = r.json()["id"]

        # Forge an admin access token for that user and register it in token store
        access = create_access_token(user_id, extra={"role": "admin"})
        store = get_token_store()
        # default ACCESS_TOKEN_EXPIRES_MIN is 15
        store.allow_access(access["jti"], user_id, ttl_seconds=60)
        headers = {"Authorization": f"Bearer {access['token']}"}

        # Now call admin-only endpoint to create another user
        r = await ac.post(
            "/api/v1/users",
            headers=headers,
            json={"email": "t@example.com", "full_name": "Target"},
        )
        assert r.status_code == 201


@pytest.mark.asyncio
async def test_refresh_rotation_invalidates_old() -> None:
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "email": "rot@example.com",
            "full_name": "Rot",
            "password": "secret123",
        }
        r = await ac.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 201
        r = await ac.post(
            "/api/v1/auth/login",
            data={"username": payload["email"], "password": payload["password"]},
        )
        tokens = r.json()
        old_refresh = tokens["refresh_token"]

        # rotate
        r = await ac.post("/api/v1/auth/refresh", params={"refresh_token": old_refresh})
        assert r.status_code == 200
        new_tokens = r.json()
        new_refresh = new_tokens["refresh_token"]

        # old refresh should be invalid now
        r = await ac.post("/api/v1/auth/refresh", params={"refresh_token": old_refresh})
        assert r.status_code == 401

        # new refresh should work
        r = await ac.post("/api/v1/auth/refresh", params={"refresh_token": new_refresh})
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_promote_user_to_admin_endpoint() -> None:
    from app.core.security import create_access_token
    from app.api.dependencies import get_token_store

    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create a normal user U1 and a separate account U2 to become admin
        r = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": "boss@example.com",
                "full_name": "Boss",
                "password": "secret123",
            },
        )
        assert r.status_code == 201
        admin_candidate_id = r.json()["id"]

        # Forge admin caller token
        forged = create_access_token(admin_candidate_id, extra={"role": "admin"})
        store = get_token_store()
        store.allow_access(forged["jti"], admin_candidate_id, ttl_seconds=60)
        headers = {"Authorization": f"Bearer {forged['token']}"}

        # Grant admin via endpoint (idempotent semantics not required here)
        r = await ac.post(
            f"/api/v1/users/{admin_candidate_id}/grant-admin", headers=headers
        )
        assert r.status_code == 200
        assert r.json()["id"] == admin_candidate_id

        # Now login as that user; returned token must carry admin role claim
        r = await ac.post(
            "/api/v1/auth/login",
            data={"username": "boss@example.com", "password": "secret123"},
        )
        assert r.status_code == 200
        tokens = r.json()
        access = tokens["access_token"]
        # admin-only endpoint should work
        r = await ac.post(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {access}"},
            json={"email": "zz@example.com", "full_name": "ZZ"},
        )
        assert r.status_code == 201


@pytest.mark.asyncio
async def test_password_reset_flow_api() -> None:
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "email": "forgot@example.com",
            "full_name": "Forgot Me",
            "password": "secret123",
        }
        r = await ac.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 201

        r = await ac.post(
            "/api/v1/auth/forgot-password", json={"email": payload["email"]}
        )
        assert r.status_code == 200
        token = r.json()["token"]
        assert token

        r = await ac.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "password": "newsecret456"},
        )
        assert r.status_code == 204

        r = await ac.post(
            "/api/v1/auth/login",
            data={"username": payload["email"], "password": payload["password"]},
        )
        assert r.status_code == 401

        r = await ac.post(
            "/api/v1/auth/login",
            data={"username": payload["email"], "password": "newsecret456"},
        )
        assert r.status_code == 200

        r = await ac.post(
            "/api/v1/auth/forgot-password", json={"email": "missing@example.com"}
        )
        assert r.status_code == 200
        assert r.json()["token"] == ""

        r = await ac.post(
            "/api/v1/auth/reset-password",
            json={"token": "invalid-token", "password": "another123"},
        )
        assert r.status_code == 400


@pytest.mark.asyncio
async def test_https_only_enforced(monkeypatch) -> None:
    # Enable HTTPS requirement and verify http requests are rejected
    import os
    from app.core.config import get_settings

    get_settings.cache_clear()  # type: ignore[attr-defined]
    os.environ["REQUIRE_HTTPS"] = "true"

    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
        assert r.status_code == 403

    # cleanup for other tests
    del os.environ["REQUIRE_HTTPS"]
    get_settings.cache_clear()  # type: ignore[attr-defined]
