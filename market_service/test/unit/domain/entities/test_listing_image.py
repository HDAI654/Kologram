from src.domain.entities.listing_image import ListingImage

LISTING = "550e8400-e29b-41d4-a716-446655440001"


def test_create_listing_image() -> None:
    img = ListingImage.create(
        listing_id=LISTING, url="https://cdn.example/a.jpg", sort_order=1
    )
    assert img.listing_id.value == LISTING
    assert img.url.value.startswith("https://")
    assert img.sort_order.value == 1
