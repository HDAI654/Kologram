"""Shared fixtures for market application unit tests (mocked infrastructure)."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.domain.entities.category import Category
from src.domain.entities.listing import Listing

SELLER_ID = "550e8400-e29b-41d4-a716-446655440000"
OTHER_SELLER_ID = "550e8400-e29b-41d4-a716-446655440099"
CATEGORY_ID = "550e8400-e29b-41d4-a716-446655440010"
LISTING_ID = "550e8400-e29b-41d4-a716-446655440020"


@pytest.fixture
def mock_uow() -> AsyncMock:
    uow = AsyncMock()
    uow.listings = AsyncMock()
    uow.categories = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    return uow


@pytest.fixture
def mock_events() -> AsyncMock:
    pub = AsyncMock()
    pub.publish = AsyncMock()
    return pub


@pytest.fixture
def active_category() -> Category:
    return Category.create(
        name="Electronics",
        id=CATEGORY_ID,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def inactive_category() -> Category:
    return Category.create(
        name="Deprecated",
        id="550e8400-e29b-41d4-a716-446655440011",
        is_active=False,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_listing(active_category: Category) -> Listing:
    return Listing.create(
        seller_id=SELLER_ID,
        category_id=active_category.id.value,
        title="MacBook Pro 14",
        description="M3, 16GB",
        price_amount="1999.00",
        quantity=1,
        location="Berlin",
        id=LISTING_ID,
    )
