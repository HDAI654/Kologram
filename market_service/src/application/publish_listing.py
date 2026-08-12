import logging
from dataclasses import dataclass

from src.domain.events.listing_published import ListingPublished
from src.domain.events.listing_status_changed import ListingStatusChanged
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.value_objects.listing_id import ListingId
from src.exceptions import SellerMismatchError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PublishListingCommand:
    listing_id: str
    seller_id: str


@dataclass(frozen=True, slots=True)
class PublishListingResult:
    listing_id: str
    status: str


class PublishListingHandler:
    """Transition a DRAFT listing to ACTIVE (publish)."""

    def __init__(
        self,
        uow: UnitOfWork,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self._uow = uow
        self._events = event_publisher

    async def handle(self, command: PublishListingCommand) -> PublishListingResult:
        logger.info("Publishing listing id=%s", command.listing_id)

        async with self._uow:
            listing = await self._uow.listings.get_by_id(ListingId(command.listing_id))
            if listing.seller_id.value != command.seller_id:
                raise SellerMismatchError("Only the listing owner may publish it")

            old_status = listing.status.value
            listing.publish()
            await self._uow.listings.update(listing)
            await self._uow.commit()

        if self._events is not None:
            await self._events.publish(
                ListingStatusChanged(
                    listing_id=listing.id.value,
                    seller_id=listing.seller_id.value,
                    old_status=old_status,
                    new_status=listing.status.value,
                )
            )
            await self._events.publish(
                ListingPublished(
                    listing_id=listing.id.value,
                    seller_id=listing.seller_id.value,
                    category_id=listing.category_id.value,
                    title=listing.title.value,
                )
            )

        logger.info("Listing published id=%s", listing.id.value)
        return PublishListingResult(
            listing_id=listing.id.value,
            status=listing.status.value,
        )
