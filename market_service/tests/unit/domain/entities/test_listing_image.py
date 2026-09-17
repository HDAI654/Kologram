import uuid

from src.domain.entities.listing_image import ListingImage
from src.domain.value_objects.image_url import ImageUrl
from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.sort_order import SortOrder


class TestListingImage:
    def test_create_with_defaults(self):
        listing_id = str(uuid.uuid4())
        url = "http://example.com/image.jpg"

        image = ListingImage.create(listing_id=listing_id, url=url)

        assert isinstance(image.id, str)
        assert uuid.UUID(image.id)  # valid UUID
        assert isinstance(image.listing_id, ListingId)
        assert image.listing_id.value == listing_id
        assert isinstance(image.url, ImageUrl)
        assert image.url.value == url
        assert isinstance(image.sort_order, SortOrder)
        assert image.sort_order.value == 0

    def test_create_with_all_fields(self):
        listing_id = str(uuid.uuid4())
        url = "http://example.com/image.jpg"
        image_id = str(uuid.uuid4())
        sort_order = 5

        image = ListingImage.create(
            listing_id=listing_id,
            url=url,
            sort_order=sort_order,
            id=image_id,
        )

        assert image.id == image_id
        assert image.listing_id.value == listing_id
        assert image.url.value == url
        assert image.sort_order.value == sort_order
