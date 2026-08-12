import logging
from dataclasses import dataclass

from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.value_objects.listing_id import ListingId

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class GetListingQuery:
    listing_id: str


@dataclass(frozen=True, slots=True)
class ListingImageItem:
    id: str
    url: str
    sort_order: int


@dataclass(frozen=True, slots=True)
class GetListingResult:
    listing_id: str
    seller_id: str
    category_id: str
    title: str
    description: str
    price_amount: str
    currency: str
    quantity: int
    status: str
    location: str
    images: list[ListingImageItem]
    created_at: str
    updated_at: str


class GetListingHandler:
    """Load a single listing by id."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: GetListingQuery) -> GetListingResult:
        async with self._uow:
            listing = await self._uow.listings.get_by_id(ListingId(query.listing_id))

        return GetListingResult(
            listing_id=listing.id.value,
            seller_id=listing.seller_id.value,
            category_id=listing.category_id.value,
            title=listing.title.value,
            description=listing.description.value,
            price_amount=str(listing.price.amount),
            currency=listing.price.currency,
            quantity=listing.quantity.value,
            status=listing.status.value,
            location=listing.location.value,
            images=[
                ListingImageItem(
                    id=img.id,
                    url=img.url.value,
                    sort_order=img.sort_order.value,
                )
                for img in sorted(listing.images, key=lambda i: i.sort_order.value)
            ],
            created_at=listing.created_at.isoformat(),
            updated_at=listing.updated_at.isoformat(),
        )
