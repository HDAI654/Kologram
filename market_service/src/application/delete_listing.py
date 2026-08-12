import logging
from dataclasses import dataclass

from src.domain.events.listing_deleted import ListingDeleted
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.value_objects.listing_id import ListingId
from src.exceptions import SellerMismatchError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DeleteListingCommand:
    listing_id: str
    seller_id: str


@dataclass(frozen=True, slots=True)
class DeleteListingResult:
    listing_id: str
    deleted: bool


class DeleteListingHandler:
    """Delete a listing owned by the seller."""

    def __init__(
        self,
        uow: UnitOfWork,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self._uow = uow
        self._events = event_publisher

    async def handle(self, command: DeleteListingCommand) -> DeleteListingResult:
        logger.info("Deleting listing id=%s", command.listing_id)

        async with self._uow:
            listing = await self._uow.listings.get_by_id(ListingId(command.listing_id))
            if listing.seller_id.value != command.seller_id:
                raise SellerMismatchError("Only the listing owner may delete it")
            listing_id = listing.id.value
            seller_id = listing.seller_id.value
            await self._uow.listings.delete(ListingId(command.listing_id))
            await self._uow.commit()

        if self._events is not None:
            await self._events.publish(
                ListingDeleted(listing_id=listing_id, seller_id=seller_id)
            )

        logger.info("Listing deleted id=%s", listing_id)
        return DeleteListingResult(listing_id=listing_id, deleted=True)
