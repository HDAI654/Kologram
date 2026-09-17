from typing import Any
from fastapi.testclient import TestClient

VERIFICATION_PATH = "/api/v1/auth/verification"
SIGNUP_PATH = "/api/v1/auth/signup"
LOGIN_PATH = "/api/v1/auth/login"
LOGOUT_PATH = "/api/v1/auth/logout"
REFRESH_PATH = "/api/v1/auth/token/refresh"


def auth_header(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def latest_verification_token(app, email: str, token_type: str = "verifyemail") -> str:
    """Read the most recent token for ``email`` from the in-memory repo.

    Real delivery is via email/broker; in dev the repo is the observation point.
    """
    repo = app.state.verification_token_repository
    target = email.lower()
    for (ttype, tvalue), stored_email in repo._store.items():
        if ttype == token_type and stored_email == target:
            return tvalue
    raise AssertionError(f"No {token_type} token for {email}")


def request_verification(client: TestClient, email: str) -> None:
    response = client.post(VERIFICATION_PATH, json={"email": email})
    assert response.status_code == 204, response.text


def signup(
    client: TestClient,
    app,
    *,
    email: str,
    password: str = "password1",
    device: str = "iPhone 15",
) -> tuple[str, str]:
    """Run verification → signup; return ``(access_token, refresh_token)``."""
    request_verification(client, email)
    token = latest_verification_token(app, email, "verifyemail")
    response = client.post(
        SIGNUP_PATH,
        json={"verify_token": token, "password": password, "device": device},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    return body["access_token"], body["refresh_token"]


def login(
    client: TestClient,
    *,
    email: str,
    password: str = "password1",
    device: str = "iPhone 15",
) -> tuple[str, str]:
    response = client.post(
        LOGIN_PATH,
        json={"email": email, "password": password, "device": device},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    return body["access_token"], body["refresh_token"]


def forget_password(client: TestClient, email: str) -> None:
    response = client.post("/api/v1/auth/password/forgot", json={"email": email})
    assert response.status_code == 204, response.text


def reset_password(client: TestClient, app, *, email: str, new_password: str) -> None:
    forget_password(client, email)
    token = latest_verification_token(app, email, "forget_pass_verify")
    response = client.post(
        "/api/v1/auth/password/reset",
        json={"verify_token": token, "new_password": new_password},
    )
    assert response.status_code == 204, response.text
