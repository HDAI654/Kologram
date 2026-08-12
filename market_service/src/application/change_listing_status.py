import logging
from dataclasses import dataclass

from src.domain.events.listing_status_changed import ListingStatusChanged
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.listing_status import ListingStatus
from src.exceptions import SellerMismatchError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ChangeListingStatusCommand:
    listing_id: str
    seller_id: str
    new_status: str


@dataclass(frozen=True, slots=True)
class ChangeListingStatusResult:
    listing_id: str
    status: str


class ChangeListingStatusHandler:
    """Apply an allowed status transition (cancel, mark sold, suspend, etc.)."""

    def __init__(
        self,
        uow: UnitOfWork,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self._uow = uow
        self._events = event_publisher

    async def handle(
        self, command: ChangeListingStatusCommand
    ) -> ChangeListingStatusResult:
        logger.info(
            "Changing listing status id=%s → %s",
            command.listing_id,
            command.new_status,
        )

        async with self._uow:
            listing = await self._uow.listings.get_by_id(ListingId(command.listing_id))
            if listing.seller_id.value != command.seller_id:
                raise SellerMismatchError(
                    "Only the listing owner may change its status"
                )

            old_status = listing.status.value
            listing.transition_to(ListingStatus(command.new_status))
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

        logger.info(
            "Listing status changed id=%s %s → %s",
            listing.id.value,
            old_status,
            listing.status.value,
        )
        return ChangeListingStatusResult(
            listing_id=listing.id.value,
            status=listing.status.value,
        )
