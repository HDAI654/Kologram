"""E2E journey: full user lifecycle across Auth Service HTTP API."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from auth_service.test.e2e.helpers import delete_json, latest_token, post_json


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_full_user_journey(client: AsyncClient, app_instance) -> None:
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Secret1A"
    new_password = "NewSecret2B"
    device_web = "web"
    device_ios = "ios"

    resp = await post_json(client, "/verification", {"email": email})
    assert resp.status_code == 204, resp.text
    token = latest_token(app_instance, "verifyemail", email)

    resp = await post_json(
        client,
        "/signup",
        {"verify_token": token, "password": password, "device": device_web},
    )
    assert resp.status_code == 201, resp.text
    pair = resp.json()
    access = pair["access_token"]
    refresh = pair["refresh_token"]
    assert access and refresh

    resp = await post_json(
        client,
        "/signup",
        {"verify_token": token, "password": password, "device": device_web},
    )
    assert resp.status_code == 400, resp.text

    resp = await post_json(
        client,
        "/login",
        {"email": email, "password": password, "device": device_ios},
    )
    assert resp.status_code == 200, resp.text
    ios_pair = resp.json()

    resp = await post_json(
        client,
        "/token/refresh",
        {"refresh_token": refresh, "device": device_web},
    )
    assert resp.status_code == 200, resp.text
    rotated = resp.json()
    access = rotated["access_token"]
    if rotated.get("refresh_token"):
        refresh = rotated["refresh_token"]

    resp = await post_json(
        client,
        "/token/refresh",
        {"refresh_token": refresh, "device": "android"},
    )
    assert resp.status_code in (401, 403), resp.text

    resp = await post_json(
        client,
        "/password",
        {"new_password": new_password, "device": device_web},
        token=access,
    )
    assert resp.status_code in (200, 204), resp.text

    resp = await post_json(
        client,
        "/login",
        {"email": email, "password": password, "device": device_web},
    )
    assert resp.status_code == 401, resp.text

    resp = await post_json(
        client,
        "/login",
        {"email": email, "password": new_password, "device": device_web},
    )
    assert resp.status_code == 200, resp.text
    access = resp.json()["access_token"]
    refresh = resp.json()["refresh_token"]

    resp = await post_json(client, "/password/forgot", {"email": email})
    assert resp.status_code == 204, resp.text
    reset_token = latest_token(app_instance, "forget_pass_verify", email)

    final_password = "FinalPass3C"
    resp = await post_json(
        client,
        "/password/reset",
        {"verify_token": reset_token, "new_password": final_password},
    )
    assert resp.status_code in (200, 204), resp.text

    resp = await post_json(
        client,
        "/login",
        {"email": email, "password": final_password, "device": device_web},
    )
    assert resp.status_code == 200, resp.text
    access = resp.json()["access_token"]
    refresh = resp.json()["refresh_token"]

    resp = await post_json(
        client,
        "/login",
        {"email": email, "password": final_password, "device": device_ios},
    )
    assert resp.status_code == 200, resp.text

    resp = await post_json(
        client,
        "/sessions/revoke-others",
        {"device": device_web},
        token=access,
    )
    assert resp.status_code == 204, resp.text

    resp = await post_json(
        client,
        "/logout",
        {"device": device_web},
        token=access,
    )
    assert resp.status_code == 204, resp.text

    resp = await post_json(
        client,
        "/token/refresh",
        {"refresh_token": refresh, "device": device_web},
    )
    assert resp.status_code in (401, 403), resp.text

    resp = await post_json(
        client,
        "/login",
        {"email": email, "password": final_password, "device": device_web},
    )
    assert resp.status_code == 200, resp.text
    access = resp.json()["access_token"]

    resp = await delete_json(
        client,
        "/account",
        {"device": device_web},
        token=access,
    )
    assert resp.status_code == 204, resp.text

    resp = await post_json(
        client,
        "/login",
        {"email": email, "password": final_password, "device": device_web},
    )
    assert resp.status_code == 401, resp.text


@pytest.mark.asyncio
async def test_signup_invalid_token(client: AsyncClient) -> None:
    resp = await post_json(
        client,
        "/signup",
        {"verify_token": str(uuid.uuid4()), "password": "Secret1A", "device": "web"},
    )
    assert resp.status_code == 400, resp.text


@pytest.mark.asyncio
async def test_signup_weak_password(client: AsyncClient, app_instance) -> None:
    email = f"weak_{uuid.uuid4().hex[:8]}@example.com"
    resp = await post_json(client, "/verification", {"email": email})
    assert resp.status_code == 204, resp.text
    token = latest_token(app_instance, "verifyemail", email)
    resp = await post_json(
        client,
        "/signup",
        {"verify_token": token, "password": "short", "device": "web"},
    )
    assert resp.status_code in (400, 422), resp.text


@pytest.mark.asyncio
async def test_login_unknown_user(client: AsyncClient) -> None:
    resp = await post_json(
        client,
        "/login",
        {
            "email": f"missing_{uuid.uuid4().hex[:8]}@example.com",
            "password": "Secret1A",
            "device": "web",
        },
    )
    assert resp.status_code == 401, resp.text


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, app_instance) -> None:
    email = f"wrongpw_{uuid.uuid4().hex[:8]}@example.com"
    password = "Secret1A"
    resp = await post_json(client, "/verification", {"email": email})
    assert resp.status_code == 204
    token = latest_token(app_instance, "verifyemail", email)
    resp = await post_json(
        client,
        "/signup",
        {"verify_token": token, "password": password, "device": "web"},
    )
    assert resp.status_code == 201, resp.text
    resp = await post_json(
        client,
        "/login",
        {"email": email, "password": "WrongPass9Z", "device": "web"},
    )
    assert resp.status_code == 401, resp.text


@pytest.mark.asyncio
async def test_protected_endpoints_require_auth(client: AsyncClient) -> None:
    resp = await post_json(client, "/logout", {"device": "web"})
    assert resp.status_code in (401, 403), resp.text
    resp = await post_json(
        client, "/password", {"new_password": "Secret1A", "device": "web"}
    )
    assert resp.status_code in (401, 403), resp.text
    resp = await delete_json(client, "/account", {"device": "web"})
    assert resp.status_code in (401, 403), resp.text


@pytest.mark.asyncio
async def test_forgot_password_unknown_email_is_silent(client: AsyncClient) -> None:
    resp = await post_json(
        client,
        "/password/forgot",
        {"email": f"ghost_{uuid.uuid4().hex[:8]}@example.com"},
    )
    assert resp.status_code == 204, resp.text


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client: AsyncClient) -> None:
    resp = await post_json(
        client,
        "/password/reset",
        {"verify_token": str(uuid.uuid4()), "new_password": "Secret1A"},
    )
    assert resp.status_code == 400, resp.text


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient) -> None:
    resp = await post_json(
        client,
        "/token/refresh",
        {"refresh_token": "not.a.valid.jwt", "device": "web"},
    )
    assert resp.status_code in (401, 403), resp.text


@pytest.mark.asyncio
async def test_revoke_session_flow(client: AsyncClient, app_instance) -> None:
    email = f"sess_{uuid.uuid4().hex[:8]}@example.com"
    password = "Secret1A"
    resp = await post_json(client, "/verification", {"email": email})
    assert resp.status_code == 204
    token = latest_token(app_instance, "verifyemail", email)
    resp = await post_json(
        client,
        "/signup",
        {"verify_token": token, "password": password, "device": "web"},
    )
    assert resp.status_code == 201
    access = resp.json()["access_token"]
    refresh = resp.json()["refresh_token"]

    resp = await post_json(
        client,
        "/login",
        {"email": email, "password": password, "device": "ios"},
    )
    assert resp.status_code == 200
    ios_refresh = resp.json()["refresh_token"]

    sessions = app_instance.state.session_repository
    ios_session_ids = [
        sid for sid, sess in sessions._by_id.items() if sess.device.value == "ios"
    ]
    assert ios_session_ids
    ios_session_id = ios_session_ids[0]

    resp = await post_json(
        client,
        "/sessions/revoke",
        {"session_id": ios_session_id, "device": "web"},
        token=access,
    )
    assert resp.status_code == 204, resp.text

    resp = await post_json(
        client,
        "/token/refresh",
        {"refresh_token": ios_refresh, "device": "ios"},
    )
    assert resp.status_code in (401, 403), resp.text

    resp = await post_json(
        client,
        "/token/refresh",
        {"refresh_token": refresh, "device": "web"},
    )
    assert resp.status_code == 200, resp.text
