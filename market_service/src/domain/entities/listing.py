from datetime import datetime, timezone

from shared.entity import Entity
from src.domain.entities.listing_image import ListingImage
from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.description import Description
from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.listing_status import ListingStatus
from src.domain.value_objects.location import Location
from src.domain.value_objects.money import Money
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.title import Title
from src.domain.value_objects.user_id import UserId
from src.exceptions import InvalidListingTransitionError, ListingNotEditableError


class Listing(Entity):
    """Listing aggregate root — sellable item offered by a seller."""

    def __init__(
        self,
        id: ListingId,
        seller_id: UserId,
        category_id: CategoryId,
        title: Title,
        description: Description,
        price: Money,
        quantity: Quantity,
        status: ListingStatus,
        location: Location,
        images: list[ListingImage],
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self.id = id
        self.seller_id = seller_id
        self.category_id = category_id
        self.title = title
        self.description = description
        self.price = price
        self.quantity = quantity
        self.status = status
        self.location = location
        self.images = list(images)
        self.created_at = created_at
        self.updated_at = updated_at
        super().__init__()

    @classmethod
    def create(
        cls,
        seller_id: str,
        category_id: str,
        title: str,
        description: str,
        price_amount: str | float | int,
        quantity: int,
        location: str,
        *,
        currency: str = "USD",
        id: str | None = None,
        status: str | None = None,
        created_at: datetime | None = None,
    ) -> "Listing":
        """Factory for a new listing (defaults to DRAFT)."""
        now = created_at or datetime.now(timezone.utc)
        return cls(
            id=ListingId(id) if id is not None else ListingId.generate(),
            seller_id=UserId(seller_id),
            category_id=CategoryId(category_id),
            title=Title(title),
            description=Description(description),
            price=Money(price_amount, currency),
            quantity=Quantity(quantity),
            status=(
                ListingStatus(status) if status is not None else ListingStatus.draft()
            ),
            location=Location(location),
            images=[],
            created_at=now,
            updated_at=now,
        )

    def update_details(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
        price_amount: str | float | int | None = None,
        currency: str | None = None,
        quantity: int | None = None,
        location: str | None = None,
        category_id: str | None = None,
    ) -> None:
        """Update mutable fields. Only allowed while status is editable."""
        if not self.status.is_editable:
            raise ListingNotEditableError(
                f"Listing in status {self.status.value} cannot be edited"
            )
        if title is not None:
            self.title = Title(title)
        if description is not None:
            self.description = Description(description)
        if price_amount is not None:
            self.price = Money(
                price_amount,
                currency if currency is not None else self.price.currency,
            )
        elif currency is not None:
            self.price = Money(self.price.amount, currency)
        if quantity is not None:
            self.quantity = Quantity(quantity)
        if location is not None:
            self.location = Location(location)
        if category_id is not None:
            self.category_id = CategoryId(category_id)
        self.updated_at = datetime.now(timezone.utc)

    def transition_to(self, new_status: ListingStatus) -> None:
        """Apply a lifecycle transition if allowed by the domain rules."""
        if not self.status.can_transition_to(new_status):
            raise InvalidListingTransitionError(
                f"Cannot transition from {self.status.value} to {new_status.value}"
            )
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def publish(self) -> None:
        """Move DRAFT → ACTIVE."""
        self.transition_to(ListingStatus.active())

    def mark_sold(self) -> None:
        self.transition_to(ListingStatus.sold())

    def cancel(self) -> None:
        self.transition_to(ListingStatus.cancelled())

    def suspend(self) -> None:
        self.transition_to(ListingStatus.suspended())

    def add_image(self, url: str, sort_order: int = 0) -> ListingImage:
        """Append an image to the aggregate."""
        if not self.status.is_editable:
            raise ListingNotEditableError(
                f"Listing in status {self.status.value} cannot be edited"
            )
        image = ListingImage.create(
            listing_id=self.id.value,
            url=url,
            sort_order=sort_order,
        )
        self.images.append(image)
        self.updated_at = datetime.now(timezone.utc)
        return image

    def clear_images(self) -> None:
        if not self.status.is_editable:
            raise ListingNotEditableError(
                f"Listing in status {self.status.value} cannot be edited"
            )
        self.images.clear()
        self.updated_at = datetime.now(timezone.utc)
