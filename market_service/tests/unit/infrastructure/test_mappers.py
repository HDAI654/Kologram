from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.user_id import UserId
from src.infrastructure.persistence.mappers import (
    category_to_domain,
    category_to_model,
    listing_to_domain,
    listing_to_model,
)
from src.infrastructure.persistence.models.listing import (
    ListingImageModel,
    ListingModel,
)


class TestCategoryMapper:
    def test_roundtrip_preserves_top_level_category(self, make_category):
        category = make_category(name="Electronics")

        model = category_to_model(category)

        assert model.id == category.id.value
        assert model.name == "Electronics"
        assert model.parent_id is None
        assert model.is_active is True
        assert model.created_at == category.created_at

        restored = category_to_domain(model)

        assert restored.id == category.id
        assert restored.name == category.name
        assert restored.parent_id is None
        assert restored.is_active is True
        assert restored.created_at == category.created_at

    def test_roundtrip_preserves_parent_and_inactive_flag(self, make_category):
        parent = make_category(name="Root Category")
        child = make_category(
            name="Leaf Category",
            parent_id=parent.id.value,
            is_active=False,
        )

        model = category_to_model(child)
        restored = category_to_domain(model)

        assert model.parent_id == parent.id.value
        assert restored.parent_id == parent.id
        assert restored.is_active is False

    def test_domain_to_model_uses_plain_string_for_parent(self, make_category):
        parent = make_category(name="Root Category")
        child = make_category(name="Leaf Category", parent_id=parent.id.value)

        model = category_to_model(child)

        assert isinstance(model.parent_id, str)
        assert model.parent_id == parent.id.value

    def test_domain_mapping_returns_typed_value_objects(self, make_category):
        category = make_category(name="Books")
        model = category_to_model(category)

        restored = category_to_domain(model)

        assert isinstance(restored.id, CategoryId)
        assert isinstance(restored.name, type(category.name))


class TestListingMapper:
    def test_roundtrip_preserves_scalar_fields(self, make_listing):
        listing = make_listing(
            title="Vintage Camera",
            description="Mint condition",
            price_amount="250.50",
            currency="EUR",
            quantity=3,
            location="Berlin",
            status="ACTIVE",
        )

        model = listing_to_model(listing)

        assert model.id == listing.id.value
        assert model.seller_id == listing.seller_id.value
        assert model.category_id == listing.category_id.value
        assert model.title == "Vintage Camera"
        assert model.description == "Mint condition"
        assert model.price_amount == Decimal("250.50")
        assert model.currency == "EUR"
        assert model.quantity == 3
        assert model.status == "ACTIVE"
        assert model.location == "Berlin"
        assert model.created_at == listing.created_at
        assert model.updated_at == listing.updated_at

        restored = listing_to_domain(model)

        assert restored.id == listing.id
        assert restored.seller_id == listing.seller_id
        assert restored.category_id == listing.category_id
        assert restored.title == listing.title
        assert restored.description == listing.description
        assert restored.price == listing.price
        assert restored.quantity == listing.quantity
        assert restored.status == listing.status
        assert restored.location == listing.location
        assert restored.created_at == listing.created_at
        assert restored.updated_at == listing.updated_at

    def test_roundtrip_preserves_images(self, make_listing):
        listing = make_listing()
        listing.add_image(url="https://example.com/a.jpg", sort_order=0)
        listing.add_image(url="https://example.com/b.jpg", sort_order=1)

        model = listing_to_model(listing)

        assert len(model.images) == 2
        assert [img.url for img in model.images] == [
            "https://example.com/a.jpg",
            "https://example.com/b.jpg",
        ]
        assert [img.sort_order for img in model.images] == [0, 1]

        restored = listing_to_domain(model)

        assert [img.url.value for img in restored.images] == [
            "https://example.com/a.jpg",
            "https://example.com/b.jpg",
        ]
        assert [img.sort_order.value for img in restored.images] == [0, 1]
        assert all(img.listing_id == restored.id for img in restored.images)

    def test_to_model_with_no_images_yields_empty_list(self, make_listing):
        listing = make_listing()
        model = listing_to_model(listing)
        assert model.images == []

    def test_to_domain_handles_missing_images_collection(self, make_listing):
        """Mapper must tolerate ``images`` being None (relationship not loaded)."""
        listing = make_listing()
        model = listing_to_model(listing)

        fake_model = MagicMock(spec=ListingModel)
        fake_model.id = model.id
        fake_model.seller_id = model.seller_id
        fake_model.category_id = model.category_id
        fake_model.title = model.title
        fake_model.description = model.description
        fake_model.price_amount = model.price_amount
        fake_model.currency = model.currency
        fake_model.quantity = model.quantity
        fake_model.status = model.status
        fake_model.location = model.location
        fake_model.created_at = model.created_at
        fake_model.updated_at = model.updated_at
        fake_model.images = None

        restored = listing_to_domain(fake_model)

        assert restored.images == []

    def test_to_model_does_not_mutate_domain_listing(self, make_listing):
        listing = make_listing()
        listing.add_image(url="https://example.com/a.jpg", sort_order=0)
        original = list(listing.images)

        listing_to_model(listing)

        assert listing.images == original

    def test_to_domain_returns_typed_value_objects(self, make_listing):
        listing = make_listing(price_amount="10.00", currency="USD")
        model = listing_to_model(listing)

        restored = listing_to_domain(model)

        assert isinstance(restored.id, ListingId)
        assert isinstance(restored.seller_id, UserId)
        assert isinstance(restored.category_id, CategoryId)
        assert restored.price.amount == Decimal("10.00")

    def test_image_models_are_detached_instances(self, make_listing):
        listing = make_listing()
        listing.add_image(url="https://example.com/a.jpg", sort_order=0)

        model = listing_to_model(listing)

        assert isinstance(model.images[0], ListingImageModel)
        assert model.images[0].id == listing.images[0].id
        assert model.images[0] is not listing.images[0]
