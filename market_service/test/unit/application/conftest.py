from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import Any
import pytest
from src.domain.entities.category import Category
from src.domain.entities.listing import Listing
from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.user_id import UserId
from src.exceptions import CategoryNotFoundError, ListingNotFoundError


class FakeEventPublisher:
    """Records events instead of delivering them."""

    def __init__(self) -> None:
        self.published: list[Any] = []

    async def publish(self, event: Any) -> None:
        self.published.append(event)


class FakeListingRepository:
    """In-memory listing repository honoring the port contract."""

    def __init__(self) -> None:
        self._items: dict[str, Listing] = {}
        self.added: list[Listing] = []
        self.updated: list[Listing] = []
        self.deleted: list[str] = []

    async def get_by_id(self, listing_id: ListingId) -> Listing:
        listing = self._items.get(listing_id.value)
        if listing is None:
            raise ListingNotFoundError(f"Listing {listing_id.value} not found")
        return listing

    async def add(self, listing: Listing) -> None:
        self._items[listing.id.value] = listing
        self.added.append(listing)

    async def update(self, listing: Listing) -> None:
        self._items[listing.id.value] = listing
        self.updated.append(listing)

    async def delete(self, listing_id: ListingId) -> None:
        self._items.pop(listing_id.value, None)
        self.deleted.append(listing_id.value)

    async def list_by_seller(
        self, seller_id: UserId, *, limit: int, offset: int
    ) -> list[Listing]:
        matches = [
            lst
            for lst in self._items.values()
            if lst.seller_id.value == seller_id.value
        ]
        return matches[offset : offset + limit]

    async def search(
        self,
        *,
        query: str | None = None,
        category_id: str | None = None,
        status: str | None = None,
        seller_id: str | None = None,
        min_price: str | None = None,
        max_price: str | None = None,
        location: str | None = None,
        limit: int,
        offset: int,
    ) -> list[Listing]:
        results = list(self._items.values())
        if query is not None:
            needle = query.lower()
            results = [lst for lst in results if needle in lst.title.value.lower()]
        if category_id is not None:
            results = [lst for lst in results if lst.category_id.value == category_id]
        if status is not None:
            results = [lst for lst in results if lst.status.value == status]
        if seller_id is not None:
            results = [lst for lst in results if lst.seller_id.value == seller_id]
        if min_price is not None:
            min_decimal = _as_decimal(min_price)
            results = [lst for lst in results if lst.price.amount >= min_decimal]
        if max_price is not None:
            max_decimal = _as_decimal(max_price)
            results = [lst for lst in results if lst.price.amount <= max_decimal]
        if location is not None:
            needle = location.lower()
            results = [lst for lst in results if needle in lst.location.value.lower()]
        return results[offset : offset + limit]


class FakeCategoryRepository:
    """In-memory category repository honoring the port contract."""

    def __init__(self) -> None:
        self._items: dict[str, Category] = {}
        self.added: list[Category] = []

    async def get_by_id(self, category_id: CategoryId) -> Category:
        category = self._items.get(category_id.value)
        if category is None:
            raise CategoryNotFoundError(f"Category {category_id.value} not found")
        return category

    async def get_by_name(self, name) -> Category | None:
        for category in self._items.values():
            if category.name.value == name.value:
                return category
        return None

    async def add(self, category: Category) -> None:
        self._items[category.id.value] = category
        self.added.append(category)

    async def list_all(self, *, active_only: bool = False) -> list[Category]:
        items = list(self._items.values())
        if active_only:
            items = [c for c in items if c.is_active]
        return items


class FakeUnitOfWork:
    """In-memory Unit of Work for application tests.

    Tracks transaction lifecycle so tests can assert commit/rollback behavior.
    """

    def __init__(self) -> None:
        self.listings = FakeListingRepository()
        self.categories = FakeCategoryRepository()
        self.committed = False
        self.commit_count = 0
        self.rolled_back = False
        self.entered = False
        self.exited = False

    async def __aenter__(self) -> "FakeUnitOfWork":
        self.entered = True
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self.exited = True
        if exc_type is not None:
            self.rolled_back = True

    async def commit(self) -> None:
        self.committed = True
        self.commit_count += 1


def _as_decimal(value: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:  # pragma: no cover
        raise AssertionError(f"Unexpected price value in test: {value!r}") from exc


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def event_publisher() -> FakeEventPublisher:
    return FakeEventPublisher()


@pytest.fixture
def make_listing():
    """Factory that produces a Listing with valid UUIDs and sensible defaults."""

    def _make(
        *,
        seller_id: str | None = None,
        category_id: str | None = None,
        status: str = "DRAFT",
        title: str = "Test Listing",
        description: str = "A description",
        price_amount: str = "100.00",
        quantity: int = 5,
        location: str = "New York",
        currency: str = "USD",
    ) -> Listing:
        return Listing.create(
            seller_id=seller_id or UserId.generate().value,
            category_id=category_id or CategoryId.generate().value,
            title=title,
            description=description,
            price_amount=price_amount,
            quantity=quantity,
            location=location,
            currency=currency,
            status=status,
        )

    return _make


@pytest.fixture
def make_category():
    def _make(
        *,
        name: str = "Electronics",
        parent_id: str | None = None,
        is_active: bool = True,
    ) -> Category:
        return Category.create(name=name, parent_id=parent_id, is_active=is_active)

    return _make
