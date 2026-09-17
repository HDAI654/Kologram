"""Shared e2e helpers for GraphQL operations."""

from __future__ import annotations

from httpx import AsyncClient


async def gql(
    client: AsyncClient,
    query: str,
    variables: dict | None = None,
) -> dict:
    """POST a GraphQL operation and return the JSON body."""
    payload: dict = {"query": query}
    if variables is not None:
        payload["variables"] = variables
    response = await client.post("/graphql", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def assert_no_errors(body: dict) -> dict:
    """Assert GraphQL response has data and no errors; return data."""
    assert "errors" not in body or body["errors"] is None, body
    assert "data" in body and body["data"] is not None, body
    return body["data"]


def assert_error_code(body: dict, code: str) -> None:
    """Assert GraphQL response carries the expected extension code."""
    assert body.get("errors"), body
    extensions = body["errors"][0].get("extensions") or {}
    assert extensions.get("code") == code, body
