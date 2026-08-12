import logging
from dataclasses import dataclass

from src.domain.events.listing_updated import ListingUpdated
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.value_objects.listing_id import ListingId
from src.exceptions import SellerMismatchError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class UpdateListingCommand:
    listing_id: str
    seller_id: str
    title: str | None = None
    description: str | None = None
    price_amount: str | None = None
    currency: str | None = None
    quantity: int | None = None
    location: str | None = None
    category_id: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateListingResult:
    listing_id: str
    status: str


class UpdateListingHandler:
    """Update mutable fields of an owned listing."""

    def __init__(
        self,
        uow: UnitOfWork,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self._uow = uow
        self._events = event_publisher

    async def handle(self, command: UpdateListingCommand) -> UpdateListingResult:
        logger.info("Updating listing id=%s", command.listing_id)

        async with self._uow:
            listing = await self._uow.listings.get_by_id(ListingId(command.listing_id))
            if listing.seller_id.value != command.seller_id:
                raise SellerMismatchError("Only the listing owner may update it")

            listing.update_details(
                title=command.title,
                description=command.description,
                price_amount=command.price_amount,
                currency=command.currency,
                quantity=command.quantity,
                location=command.location,
                category_id=command.category_id,
            )
            await self._uow.listings.update(listing)
            await self._uow.commit()

        if self._events is not None:
            await self._events.publish(
                ListingUpdated(
                    listing_id=listing.id.value,
                    seller_id=listing.seller_id.value,
                )
            )

        logger.info("Listing updated id=%s", listing.id.value)
        return UpdateListingResult(
            listing_id=listing.id.value,
            status=listing.status.value,
        )
