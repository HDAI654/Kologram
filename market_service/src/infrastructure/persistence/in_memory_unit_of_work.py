"""In-memory Unit of Work for unit / e2e tests without a real database."""

from __future__ import annotations

import logging
from types import TracebackType

from src.domain.entities.category import Category
from src.domain.entities.listing import Listing
from src.domain.ports.category_repository import CategoryRepository
from src.domain.ports.listing_repository import ListingRepository
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.category_name import CategoryName
from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.user_id import UserId
from src.exceptions import CategoryNotFoundError, ListingNotFoundError

logger = logging.getLogger(__name__)


class InMemoryCategoryRepository(CategoryRepository):
    def __init__(self, store: dict[str, Category]) -> None:
        self._store = store

    async def add(self, category: Category) -> None:
        self._store[category.id.value] = category

    async def get_by_id(self, category_id: CategoryId) -> Category:
        cat = self._store.get(category_id.value)
        if cat is None:
            logger.debug("Category not found id=%s", category_id.value)
            raise CategoryNotFoundError(f"Category '{category_id.value}' not found")
        return cat

    async def get_by_name(self, name: CategoryName) -> Category | None:
        for cat in self._store.values():
            if cat.name == name:
                return cat
        return None

    async def update(self, category: Category) -> None:
        if category.id.value not in self._store:
            raise CategoryNotFoundError(f"Category '{category.id.value}' not found")
        self._store[category.id.value] = category

    async def list_all(self, *, active_only: bool = False) -> list[Category]:
        items = list(self._store.values())
        if active_only:
            items = [c for c in items if c.is_active]
        return sorted(items, key=lambda c: c.name.value)

    async def list_children(self, parent_id: CategoryId) -> list[Category]:
        return [
            c
            for c in self._store.values()
            if c.parent_id is not None and c.parent_id == parent_id
        ]


class InMemoryListingRepository(ListingRepository):
    def __init__(self, store: dict[str, Listing]) -> None:
        self._store = store

    async def add(self, listing: Listing) -> None:
        self._store[listing.id.value] = listing

    async def get_by_id(self, listing_id: ListingId) -> Listing:
        lst = self._store.get(listing_id.value)
        if lst is None:
            logger.debug("Listing not found id=%s", listing_id.value)
            raise ListingNotFoundError(f"Listing '{listing_id.value}' not found")
        return lst

    async def update(self, listing: Listing) -> None:
        if listing.id.value not in self._store:
            raise ListingNotFoundError(f"Listing '{listing.id.value}' not found")
        self._store[listing.id.value] = listing

    async def delete(self, listing_id: ListingId) -> None:
        if listing_id.value not in self._store:
            raise ListingNotFoundError(f"Listing '{listing_id.value}' not found")
        del self._store[listing_id.value]

    async def list_by_seller(
        self,
        seller_id: UserId,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Listing]:
        items = [l for l in self._store.values() if l.seller_id == seller_id]
        items.sort(key=lambda l: l.created_at, reverse=True)
        return items[offset : offset + limit]

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
        limit: int = 20,
        offset: int = 0,
    ) -> list[Listing]:
        items = list(self._store.values())
        if query:
            q = query.lower()
            items = [
                l
                for l in items
                if q in l.title.value.lower() or q in l.description.value.lower()
            ]
        if category_id:
            items = [l for l in items if l.category_id.value == category_id]
        if status:
            items = [l for l in items if l.status.value == status.upper()]
        if seller_id:
            items = [l for l in items if l.seller_id.value == seller_id]
        if min_price is not None:
            from decimal import Decimal

            mn = Decimal(min_price)
            items = [l for l in items if l.price.amount >= mn]
        if max_price is not None:
            from decimal import Decimal

            mx = Decimal(max_price)
            items = [l for l in items if l.price.amount <= mx]
        if location:
            loc = location.lower()
            items = [l for l in items if loc in l.location.value.lower()]
        items.sort(key=lambda l: l.created_at, reverse=True)
        return items[offset : offset + limit]


class InMemoryUnitOfWork(UnitOfWork):
    """Shared in-memory stores across a single UoW instance (test helper)."""

    def __init__(
        self,
        listings: dict[str, Listing] | None = None,
        categories: dict[str, Category] | None = None,
    ) -> None:
        self._listings = listings if listings is not None else {}
        self._categories = categories if categories is not None else {}
        self.listings = InMemoryListingRepository(self._listings)
        self.categories = InMemoryCategoryRepository(self._categories)

    async def __aenter__(self) -> "InMemoryUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass
