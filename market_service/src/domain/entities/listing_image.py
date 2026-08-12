from shared.entity import Entity
from src.domain.value_objects.image_url import ImageUrl
from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.sort_order import SortOrder


class ListingImage(Entity):
    """Child entity: an image belonging to a listing aggregate."""

    def __init__(
        self,
        id: str,
        listing_id: ListingId,
        url: ImageUrl,
        sort_order: SortOrder,
    ) -> None:
        self.id = id
        self.listing_id = listing_id
        self.url = url
        self.sort_order = sort_order
        super().__init__()

    @classmethod
    def create(
        cls,
        listing_id: str,
        url: str,
        sort_order: int = 0,
        *,
        id: str | None = None,
    ) -> "ListingImage":
        """Factory for a new listing image."""
        import uuid

        return cls(
            id=id if id is not None else str(uuid.uuid4()),
            listing_id=ListingId(listing_id),
            url=ImageUrl(url),
            sort_order=SortOrder(sort_order),
        )
