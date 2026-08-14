"""Shared e2e helpers for Auth Service HTTP flows."""

from __future__ import annotations

from typing import Any

from httpx import AsyncClient, Response

BASE = "/api/v1/auth"


async def post_json(
    client: AsyncClient,
    path: str,
    body: dict[str, Any] | None = None,
    *,
    token: str | None = None,
) -> Response:
    headers: dict[str, str] = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    return await client.post(f"{BASE}{path}", json=body or {}, headers=headers)


async def delete_json(
    client: AsyncClient,
    path: str,
    body: dict[str, Any] | None = None,
    *,
    token: str | None = None,
) -> Response:
    headers: dict[str, str] = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    return await client.request(
        "DELETE", f"{BASE}{path}", json=body or {}, headers=headers
    )


def latest_token(app, token_type: str, email: str | None = None) -> str:
    """Read the most recently stored verification token from in-memory store."""
    store: dict[tuple[str, str], str] = app.state.verification_token_repository._store
    matches = [
        (tok, em)
        for (tt, tok), em in store.items()
        if tt == token_type and (email is None or em == email)
    ]
    assert matches, f"No token of type={token_type!r} for email={email!r} in {store}"
    return matches[-1][0]
