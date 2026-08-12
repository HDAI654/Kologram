"""List listings owned by a seller."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.value_objects.user_id import UserId

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ListSellerListingsQuery:
    seller_id: str
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True, slots=True)
class SellerListingItem:
    listing_id: str
    seller_id: str
    category_id: str
    title: str
    status: str
    price_amount: str
    currency: str
    location: str
    created_at: str


@dataclass(frozen=True, slots=True)
class ListSellerListingsResult:
    items: tuple[SellerListingItem, ...]


class ListSellerListingsHandler:
    """Return paginated listings for a seller."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: ListSellerListingsQuery) -> ListSellerListingsResult:
        limit = query.limit if query.limit > 0 else 50
        offset = max(query.offset, 0)
        logger.info(
            "Listing seller listings seller_id=%s limit=%s offset=%s",
            query.seller_id,
            limit,
            offset,
        )
        async with self._uow:
            listings = await self._uow.listings.list_by_seller(
                UserId(query.seller_id), limit=limit, offset=offset
            )
        items = tuple(
            SellerListingItem(
                listing_id=lst.id.value,
                seller_id=lst.seller_id.value,
                category_id=lst.category_id.value,
                title=lst.title.value,
                status=lst.status.value,
                price_amount=str(lst.price.amount),
                currency=lst.price.currency,
                location=lst.location.value,
                created_at=lst.created_at.isoformat(),
            )
            for lst in listings
        )
        logger.info("Found %s listings for seller_id=%s", len(items), query.seller_id)
        return ListSellerListingsResult(items=items)
