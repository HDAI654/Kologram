import logging
from dataclasses import dataclass

from src.domain.entities.listing import Listing
from src.domain.events.listing_created import ListingCreated
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.value_objects.category_id import CategoryId
from src.exceptions import CategoryInactiveError, CategoryNotFoundError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CreateListingCommand:
    seller_id: str
    category_id: str
    title: str
    description: str
    price_amount: str
    quantity: int
    location: str
    currency: str = "USD"
    image_urls: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CreateListingResult:
    listing_id: str
    status: str


class CreateListingHandler:
    """Create a new listing in DRAFT status for the authenticated seller."""

    def __init__(
        self,
        uow: UnitOfWork,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self._uow = uow
        self._events = event_publisher

    async def handle(self, command: CreateListingCommand) -> CreateListingResult:
        logger.info(
            "Creating listing seller_id=%s category_id=%s",
            command.seller_id,
            command.category_id,
        )

        async with self._uow:
            try:
                category = await self._uow.categories.get_by_id(
                    CategoryId(command.category_id)
                )
            except CategoryNotFoundError as exc:
                raise CategoryNotFoundError(
                    f"Category '{command.category_id}' not found"
                ) from exc

            if not category.is_active:
                raise CategoryInactiveError(
                    f"Category '{command.category_id}' is inactive"
                )

            listing = Listing.create(
                seller_id=command.seller_id,
                category_id=command.category_id,
                title=command.title,
                description=command.description,
                price_amount=command.price_amount,
                quantity=command.quantity,
                location=command.location,
                currency=command.currency,
            )

            for idx, url in enumerate(command.image_urls):
                listing.add_image(url=url, sort_order=idx)

            await self._uow.listings.add(listing)
            await self._uow.commit()

        if self._events is not None:
            await self._events.publish(
                ListingCreated(
                    listing_id=listing.id.value,
                    seller_id=listing.seller_id.value,
                    category_id=listing.category_id.value,
                    title=listing.title.value,
                    status=listing.status.value,
                )
            )

        logger.info("Listing created id=%s", listing.id.value)
        return CreateListingResult(
            listing_id=listing.id.value,
            status=listing.status.value,
        )
