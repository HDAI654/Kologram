import logging
from dataclasses import dataclass

from src.domain.ports.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SearchListingsQuery:
    query: str | None = None
    category_id: str | None = None
    status: str | None = "ACTIVE"
    seller_id: str | None = None
    min_price: str | None = None
    max_price: str | None = None
    location: str | None = None
    limit: int = 20
    offset: int = 0


@dataclass(frozen=True, slots=True)
class ListingSnapshotItem:
    listing_id: str
    seller_id: str
    category_id: str
    title: str
    price_amount: str
    currency: str
    status: str
    location: str
    created_at: str


@dataclass(frozen=True, slots=True)
class SearchListingsResult:
    items: list[ListingSnapshotItem]
    limit: int
    offset: int


class SearchListingsHandler:
    """Search / filter listings (read model style snapshots)."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: SearchListingsQuery) -> SearchListingsResult:
        limit = max(1, min(query.limit, 100))
        offset = max(0, query.offset)

        async with self._uow:
            listings = await self._uow.listings.search(
                query=query.query,
                category_id=query.category_id,
                status=query.status,
                seller_id=query.seller_id,
                min_price=query.min_price,
                max_price=query.max_price,
                location=query.location,
                limit=limit,
                offset=offset,
            )

        items = [
            ListingSnapshotItem(
                listing_id=lst.id.value,
                seller_id=lst.seller_id.value,
                category_id=lst.category_id.value,
                title=lst.title.value,
                price_amount=str(lst.price.amount),
                currency=lst.price.currency,
                status=lst.status.value,
                location=lst.location.value,
                created_at=lst.created_at.isoformat(),
            )
            for lst in listings
        ]
        return SearchListingsResult(items=items, limit=limit, offset=offset)
