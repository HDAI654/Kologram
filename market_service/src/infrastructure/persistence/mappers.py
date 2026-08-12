"""Map between domain aggregates and SQLAlchemy models."""

from src.domain.entities.category import Category
from src.domain.entities.listing import Listing
from src.domain.entities.listing_image import ListingImage
from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.category_name import CategoryName
from src.domain.value_objects.description import Description
from src.domain.value_objects.image_url import ImageUrl
from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.listing_status import ListingStatus
from src.domain.value_objects.location import Location
from src.domain.value_objects.money import Money
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.sort_order import SortOrder
from src.domain.value_objects.title import Title
from src.domain.value_objects.user_id import UserId
from src.infrastructure.persistence.models.category import CategoryModel
from src.infrastructure.persistence.models.listing import (
    ListingImageModel,
    ListingModel,
)


def category_to_model(category: Category) -> CategoryModel:
    return CategoryModel(
        id=category.id.value,
        name=category.name.value,
        parent_id=category.parent_id.value if category.parent_id else None,
        is_active=category.is_active,
        created_at=category.created_at,
    )


def category_to_domain(model: CategoryModel) -> Category:
    return Category(
        id=CategoryId(model.id),
        name=CategoryName(model.name),
        parent_id=CategoryId(model.parent_id) if model.parent_id else None,
        is_active=model.is_active,
        created_at=model.created_at,
    )


def listing_to_model(listing: Listing) -> ListingModel:
    model = ListingModel(
        id=listing.id.value,
        seller_id=listing.seller_id.value,
        category_id=listing.category_id.value,
        title=listing.title.value,
        description=listing.description.value,
        price_amount=listing.price.amount,
        currency=listing.price.currency,
        quantity=listing.quantity.value,
        status=listing.status.value,
        location=listing.location.value,
        created_at=listing.created_at,
        updated_at=listing.updated_at,
    )
    model.images = [
        ListingImageModel(
            id=img.id,
            listing_id=listing.id.value,
            url=img.url.value,
            sort_order=img.sort_order.value,
        )
        for img in listing.images
    ]
    return model


def listing_to_domain(model: ListingModel) -> Listing:
    images = [
        ListingImage(
            id=img.id,
            listing_id=ListingId(model.id),
            url=ImageUrl(img.url),
            sort_order=SortOrder(img.sort_order),
        )
        for img in (model.images or [])
    ]
    return Listing(
        id=ListingId(model.id),
        seller_id=UserId(model.seller_id),
        category_id=CategoryId(model.category_id),
        title=Title(model.title),
        description=Description(model.description),
        price=Money(model.price_amount, model.currency),
        quantity=Quantity(model.quantity),
        status=ListingStatus(model.status),
        location=Location(model.location),
        images=images,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
