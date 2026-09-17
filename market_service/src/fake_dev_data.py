_DEV_SELLER_ID = "ec887b84-ef6b-4137-b7bd-8bcb83cf2f61"

_DEV_ELECTRONICS_ID = "34567b47-485f-41e0-9821-7ddac63603c4"
_DEV_LAPTOPS_ID = "e2c8ebb5-2c85-4803-b680-30014786b6a3"
_DEV_FURNITURE_ID = "40bde861-e59c-452a-bce4-74b3a2ff1582"


def _seed_dev_categories(store: dict) -> None:
    from src.domain.entities.category import Category

    electronics = Category.create(
        name="Electronics", id=_DEV_ELECTRONICS_ID, is_active=True
    )
    laptops = Category.create(
        name="Laptops",
        id=_DEV_LAPTOPS_ID,
        parent_id=_DEV_ELECTRONICS_ID,
        is_active=True,
    )
    furniture = Category.create(
        name="Furniture",
        id=_DEV_FURNITURE_ID,
        is_active=False,
    )
    for category in (electronics, laptops, furniture):
        store[category.id.value] = category


def _seed_dev_listings(store: dict) -> None:
    from src.domain.entities.listing import Listing

    camera = Listing.create(
        seller_id=_DEV_SELLER_ID,
        category_id=_DEV_ELECTRONICS_ID,
        title="Vintage Film Camera",
        description="Fully working, minor wear on the body.",
        price_amount="249.99",
        currency="USD",
        quantity=1,
        location="Berlin",
        status="ACTIVE",
    )
    camera.add_image(url="https://example.com/camera-front.jpg", sort_order=0)
    camera.add_image(url="https://example.com/camera-back.jpg", sort_order=1)

    laptop = Listing.create(
        seller_id=_DEV_SELLER_ID,
        category_id=_DEV_LAPTOPS_ID,
        title="ThinkPad X1 Carbon",
        description="14 inch, 16GB RAM, 512GB SSD.",
        price_amount="1299.00",
        currency="EUR",
        quantity=3,
        location="Amsterdam",
        status="DRAFT",
    )

    for listing in (camera, laptop):
        store[listing.id.value] = listing