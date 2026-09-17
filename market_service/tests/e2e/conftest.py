from __future__ import annotations

import os

# Must run before importing src.app: src.conf captures env at import time.
os.environ["APP_NAME"] = "Kologram-E2E"
os.environ["APP_ENV"] = "development"
os.environ["RABBITMQ_ENABLED"] = "false"

from typing import Callable

import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.fake_dev_data import (
    _seed_dev_categories,
    _seed_dev_listings,
)

GraphqlCall = Callable[[str, dict | None], dict]


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def _reset_in_memory_stores() -> None:
    uow = app.state.uow()
    uow.listings._store.clear()
    uow.categories._store.clear()
    _seed_dev_categories(uow.categories._store)
    _seed_dev_listings(uow.listings._store)
    yield


@pytest.fixture
def gql(client: TestClient) -> GraphqlCall:
    def _gql(query: str, variables: dict | None = None) -> dict:
        response = client.post(
            "/graphql",
            json={"query": query, "variables": variables or {}},
        )
        assert response.status_code == 200, response.text
        return response.json()

    return _gql


@pytest.fixture
def seeded_camera_id(gql: GraphqlCall) -> str:
    """Return the listing id of the seeded 'Vintage Film Camera'."""
    result = gql("""
        query {
            searchListings(input: {status: "ACTIVE", query: "Vintage"}) {
                items { listingId title }
            }
        }
        """)
    items = result["data"]["searchListings"]["items"]
    camera = next(i for i in items if i["title"] == "Vintage Film Camera")
    return camera["listingId"]
