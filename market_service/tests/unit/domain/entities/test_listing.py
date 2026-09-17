import time
from datetime import datetime, timezone
import uuid
import pytest

from src.domain.entities.listing import Listing
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


@pytest.fixture
def listing_data():
    return {
        "seller_id": str(uuid.uuid4()),
        "category_id": str(uuid.uuid4()),
        "title": "Test Listing",
        "description": "A test description",
        "price_amount": 100.0,
        "quantity": 5,
        "location": "New York",
        "currency": "USD",
    }


@pytest.fixture
def listing(listing_data):
    return Listing.create(**listing_data)


class TestListing:
    def test_create_with_required_fields(self, listing_data):
        listing = Listing.create(**listing_data)

        assert isinstance(listing.id, ListingId)
        assert isinstance(listing.seller_id, UserId)
        assert listing.seller_id.value == listing_data["seller_id"]
        assert isinstance(listing.category_id, CategoryId)
        assert listing.category_id.value == listing_data["category_id"]
        assert isinstance(listing.title, Title)
        assert listing.title.value == listing_data["title"]
        assert isinstance(listing.description, Description)
        assert listing.description.value == listing_data["description"]
        assert isinstance(listing.price, Money)
        assert listing.price.amount == listing_data["price_amount"]
        assert listing.price.currency == listing_data["currency"]
        assert isinstance(listing.quantity, Quantity)
        assert listing.quantity.value == listing_data["quantity"]
        assert listing.status == ListingStatus.draft()
        assert isinstance(listing.location, Location)
        assert listing.location.value == listing_data["location"]
        assert listing.images == []
        assert isinstance(listing.created_at, datetime)
        assert isinstance(listing.updated_at, datetime)
        assert listing.created_at == listing.updated_at

    def test_create_with_all_fields(self, listing_data):
        created_at = datetime(2023, 1, 1, tzinfo=timezone.utc)
        listing_id = ListingId.generate()
        listing = Listing.create(
            **listing_data,
            id=listing_id.value,
            status="active",
            created_at=created_at,
        )

        assert listing.id == listing_id
        assert listing.status == ListingStatus.active()
        assert listing.created_at == created_at
        assert listing.updated_at == created_at

    def test_update_details_while_editable(self, listing):
        original_updated_at = listing.updated_at
        time.sleep(0.001)

        _category_id = str(uuid.uuid4())

        listing.update_details(
            title="New Title",
            description="New Description",
            price_amount=200.0,
            currency="EUR",
            quantity=10,
            location="London",
            category_id=_category_id,
        )

        assert listing.title.value == "New Title"
        assert listing.description.value == "New Description"
        assert listing.price.amount == 200.0
        assert listing.price.currency == "EUR"
        assert listing.quantity.value == 10
        assert listing.location.value == "London"
        assert listing.category_id.value == _category_id
        assert listing.updated_at > original_updated_at

    def test_update_details_when_not_editable_raises(self, listing_data):
        listing = Listing.create(**listing_data, status="sold")
        with pytest.raises(ListingNotEditableError):
            listing.update_details(title="New Title")

    def test_update_details_partial(self, listing):
        original_title = listing.title.value
        original_description = listing.description.value

        listing.update_details(title="New Title")

        assert listing.title.value == "New Title"
        assert listing.description.value == original_description

    def test_update_details_price_amount_without_currency(self, listing):
        original_currency = listing.price.currency
        listing.update_details(price_amount=150.0)
        assert listing.price.amount == 150.0
        assert listing.price.currency == original_currency

    def test_update_details_currency_without_price_amount(self, listing):
        original_amount = listing.price.amount
        listing.update_details(currency="GBP")
        assert listing.price.amount == original_amount
        assert listing.price.currency == "GBP"

    def test_transition_to_valid(self, listing):
        original_updated_at = listing.updated_at
        time.sleep(0.001)

        listing.transition_to(ListingStatus.active())

        assert listing.status == ListingStatus.active()
        assert listing.updated_at > original_updated_at

    def test_transition_to_invalid_raises(self, listing):
        # DRAFT → SOLD is not a valid transition
        with pytest.raises(InvalidListingTransitionError):
            listing.transition_to(ListingStatus.sold())

    def test_publish(self, listing):
        listing.publish()
        assert listing.status == ListingStatus.active()

    def test_mark_sold(self, listing_data):
        listing = Listing.create(**listing_data, status="active")
        listing.mark_sold()
        assert listing.status == ListingStatus.sold()

    def test_cancel(self, listing):
        listing.cancel()
        assert listing.status == ListingStatus.cancelled()

    def test_suspend(self, listing_data):
        listing = Listing.create(**listing_data, status="active")
        listing.suspend()
        assert listing.status == ListingStatus.suspended()

    def test_add_image_while_editable(self, listing):
        original_updated_at = listing.updated_at
        time.sleep(0.001)

        image = listing.add_image(url="http://example.com/image.jpg", sort_order=1)

        assert len(listing.images) == 1
        assert listing.images[0] == image
        assert isinstance(image, ListingImage)
        assert image.listing_id.value == listing.id.value
        assert image.url.value == "http://example.com/image.jpg"
        assert image.sort_order.value == 1
        assert listing.updated_at > original_updated_at

    def test_add_image_when_not_editable_raises(self, listing_data):
        listing = Listing.create(**listing_data, status="sold")
        with pytest.raises(ListingNotEditableError):
            listing.add_image(url="http://example.com/image.jpg")

    def test_clear_images_while_editable(self, listing):
        listing.add_image(url="http://example.com/image1.jpg")
        listing.add_image(url="http://example.com/image2.jpg")
        assert len(listing.images) == 2

        original_updated_at = listing.updated_at
        time.sleep(0.001)

        listing.clear_images()

        assert listing.images == []
        assert listing.updated_at > original_updated_at

    def test_clear_images_when_not_editable_raises(self, listing_data):
        listing = Listing.create(**listing_data, status="sold")
        with pytest.raises(ListingNotEditableError):
            listing.clear_images()
