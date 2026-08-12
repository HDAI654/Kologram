"""Strawberry GraphQL types — presentation DTOs only."""

from __future__ import annotations

import strawberry

# ---------------------------------------------------------------------------
# Object types
# ---------------------------------------------------------------------------


@strawberry.type(description="Category aggregate projection.")
class CategoryType:
    category_id: str
    name: str
    parent_id: str | None
    is_active: bool
    created_at: str


@strawberry.type(description="Image attached to a listing.")
class ListingImageType:
    id: str
    url: str
    sort_order: int


@strawberry.type(description="Full listing detail.")
class ListingType:
    listing_id: str
    seller_id: str
    category_id: str
    title: str
    description: str
    price_amount: str
    currency: str
    quantity: int
    status: str
    location: str
    images: list[ListingImageType]
    created_at: str
    updated_at: str


@strawberry.type(description="Listing search / list snapshot.")
class ListingSnapshotType:
    listing_id: str
    seller_id: str
    category_id: str
    title: str
    price_amount: str
    currency: str
    status: str
    location: str
    created_at: str


@strawberry.type(description="Paginated listing search result.")
class SearchListingsResultType:
    items: list[ListingSnapshotType]
    limit: int
    offset: int


# ---------------------------------------------------------------------------
# Mutation payloads
# ---------------------------------------------------------------------------


@strawberry.type
class CreateListingPayload:
    listing_id: str
    status: str


@strawberry.type
class UpdateListingPayload:
    listing_id: str
    status: str


@strawberry.type
class DeleteListingPayload:
    listing_id: str
    deleted: bool


@strawberry.type
class PublishListingPayload:
    listing_id: str
    status: str


@strawberry.type
class ChangeListingStatusPayload:
    listing_id: str
    status: str


@strawberry.type
class CreateCategoryPayload:
    category_id: str
    name: str
    parent_id: str | None
    is_active: bool


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


@strawberry.input
class CreateListingInput:
    seller_id: str
    category_id: str
    title: str
    description: str = ""
    price_amount: str = "0"
    currency: str = "USD"
    quantity: int = 1
    location: str = ""
    image_urls: list[str] | None = None


@strawberry.input
class UpdateListingInput:
    listing_id: str
    seller_id: str
    title: str | None = None
    description: str | None = None
    price_amount: str | None = None
    currency: str | None = None
    quantity: int | None = None
    location: str | None = None
    category_id: str | None = None


@strawberry.input
class DeleteListingInput:
    listing_id: str
    seller_id: str


@strawberry.input
class PublishListingInput:
    listing_id: str
    seller_id: str


@strawberry.input
class ChangeListingStatusInput:
    listing_id: str
    seller_id: str
    new_status: str


@strawberry.input
class CreateCategoryInput:
    name: str
    parent_id: str | None = None


@strawberry.input
class SearchListingsInput:
    query: str | None = None
    category_id: str | None = None
    status: str | None = "ACTIVE"
    seller_id: str | None = None
    min_price: str | None = None
    max_price: str | None = None
    location: str | None = None
    limit: int = 20
    offset: int = 0
