import pytest

from src.domain.entities.listing import Listing
from src.exceptions import ListingNotEditableError

SELLER = "550e8400-e29b-41d4-a716-446655440000"
CATEGORY = "550e8400-e29b-41d4-a716-446655440001"


def test_create_defaults_to_draft() -> None:
    listing = Listing.create(
        seller_id=SELLER,
        category_id=CATEGORY,
        title="Old Bike",
        description="Good condition",
        price_amount="50",
        quantity=1,
        location="Ankara",
    )
    assert listing.status.value == "DRAFT"
    assert listing.images == []


def test_add_image() -> None:
    listing = Listing.create(
        seller_id=SELLER,
        category_id=CATEGORY,
        title="Old Bike",
        description="",
        price_amount="50",
        quantity=1,
        location="Ankara",
    )
    img = listing.add_image("https://cdn.example.com/bike.jpg", sort_order=1)
    assert len(listing.images) == 1
    assert img.url.value.startswith("https://")


def test_update_details() -> None:
    listing = Listing.create(
        seller_id=SELLER,
        category_id=CATEGORY,
        title="Old Bike",
        description="",
        price_amount="50",
        quantity=1,
        location="Ankara",
    )
    listing.update_details(title="Road Bike Pro", price_amount="75.50", quantity=2)
    assert listing.title.value == "Road Bike Pro"
    assert str(listing.price.amount) == "75.50"
    assert listing.quantity.value == 2


def test_cannot_add_image_when_sold() -> None:
    listing = Listing.create(
        seller_id=SELLER,
        category_id=CATEGORY,
        title="Old Bike",
        description="",
        price_amount="50",
        quantity=1,
        location="Ankara",
    )
    listing.publish()
    listing.mark_sold()
    with pytest.raises(ListingNotEditableError):
        listing.add_image("https://cdn.example.com/x.jpg")
