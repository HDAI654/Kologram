"""Strawberry GraphQL schema — Market Service presentation layer."""

from __future__ import annotations

import logging

import strawberry
from strawberry.types import Info

from src.application.change_listing_status import (
    ChangeListingStatusCommand,
    ChangeListingStatusHandler,
)
from src.application.create_category import CreateCategoryCommand, CreateCategoryHandler
from src.application.create_listing import CreateListingCommand, CreateListingHandler
from src.application.delete_listing import DeleteListingCommand, DeleteListingHandler
from src.application.get_listing import GetListingHandler, GetListingQuery
from src.application.list_categories import ListCategoriesHandler, ListCategoriesQuery
from src.application.list_seller_listings import (
    ListSellerListingsHandler,
    ListSellerListingsQuery,
)
from src.application.publish_listing import PublishListingCommand, PublishListingHandler
from src.application.search_listings import SearchListingsHandler, SearchListingsQuery
from src.application.update_listing import UpdateListingCommand, UpdateListingHandler
from src.presentation.graphql.errors import raise_graphql_error
from src.presentation.graphql.types import (
    CategoryType,
    ChangeListingStatusInput,
    ChangeListingStatusPayload,
    CreateCategoryInput,
    CreateCategoryPayload,
    CreateListingInput,
    CreateListingPayload,
    DeleteListingInput,
    DeleteListingPayload,
    ListingImageType,
    ListingSnapshotType,
    ListingType,
    PublishListingInput,
    PublishListingPayload,
    SearchListingsInput,
    SearchListingsResultType,
    UpdateListingInput,
    UpdateListingPayload,
)

logger = logging.getLogger(__name__)


@strawberry.type
class Query:
    """Read-side operations."""

    @strawberry.field(description="Fetch a single listing by id.")
    async def listing(self, info: Info, listing_id: str) -> ListingType:
        handler = GetListingHandler(info.context["uow_factory"]())
        try:
            result = await handler.handle(GetListingQuery(listing_id=listing_id))
        except Exception as exc:
            raise_graphql_error(exc)
        return ListingType(
            listing_id=result.listing_id,
            seller_id=result.seller_id,
            category_id=result.category_id,
            title=result.title,
            description=result.description,
            price_amount=result.price_amount,
            currency=result.currency,
            quantity=result.quantity,
            status=result.status,
            location=result.location,
            images=[
                ListingImageType(id=img.id, url=img.url, sort_order=img.sort_order)
                for img in result.images
            ],
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    @strawberry.field(description="Search and filter listings.")
    async def search_listings(
        self,
        info: Info,
        input: SearchListingsInput | None = None,
    ) -> SearchListingsResultType:
        params = input or SearchListingsInput()
        handler = SearchListingsHandler(info.context["uow_factory"]())
        try:
            result = await handler.handle(
                SearchListingsQuery(
                    query=params.query,
                    category_id=params.category_id,
                    status=params.status,
                    seller_id=params.seller_id,
                    min_price=params.min_price,
                    max_price=params.max_price,
                    location=params.location,
                    limit=params.limit,
                    offset=params.offset,
                )
            )
        except Exception as exc:
            raise_graphql_error(exc)
        return SearchListingsResultType(
            items=[
                ListingSnapshotType(
                    listing_id=i.listing_id,
                    seller_id=i.seller_id,
                    category_id=i.category_id,
                    title=i.title,
                    price_amount=i.price_amount,
                    currency=i.currency,
                    status=i.status,
                    location=i.location,
                    created_at=i.created_at,
                )
                for i in result.items
            ],
            limit=result.limit,
            offset=result.offset,
        )

    @strawberry.field(description="List listings owned by a seller.")
    async def seller_listings(
        self,
        info: Info,
        seller_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ListingSnapshotType]:
        handler = ListSellerListingsHandler(info.context["uow_factory"]())
        try:
            result = await handler.handle(
                ListSellerListingsQuery(seller_id=seller_id, limit=limit, offset=offset)
            )
        except Exception as exc:
            raise_graphql_error(exc)
        return [
            ListingSnapshotType(
                listing_id=i.listing_id,
                seller_id=i.seller_id,
                category_id=i.category_id,
                title=i.title,
                price_amount=i.price_amount,
                currency=i.currency,
                status=i.status,
                location=i.location,
                created_at=i.created_at,
            )
            for i in result.items
        ]

    @strawberry.field(description="List categories (optionally active only).")
    async def categories(
        self,
        info: Info,
        active_only: bool = False,
    ) -> list[CategoryType]:
        handler = ListCategoriesHandler(info.context["uow_factory"]())
        try:
            result = await handler.handle(ListCategoriesQuery(active_only=active_only))
        except Exception as exc:
            raise_graphql_error(exc)
        return [
            CategoryType(
                category_id=i.category_id,
                name=i.name,
                parent_id=i.parent_id,
                is_active=i.is_active,
                created_at=i.created_at,
            )
            for i in result.items
        ]


@strawberry.type
class Mutation:
    """Write-side operations."""

    @strawberry.mutation(description="Create a new listing in DRAFT status.")
    async def create_listing(
        self, info: Info, input: CreateListingInput
    ) -> CreateListingPayload:
        handler = CreateListingHandler(
            info.context["uow_factory"](), info.context["event_publisher"]
        )
        try:
            result = await handler.handle(
                CreateListingCommand(
                    seller_id=input.seller_id,
                    category_id=input.category_id,
                    title=input.title,
                    description=input.description,
                    price_amount=input.price_amount,
                    currency=input.currency,
                    quantity=input.quantity,
                    location=input.location,
                    image_urls=tuple(input.image_urls or ()),
                )
            )
        except Exception as exc:
            raise_graphql_error(exc)
        return CreateListingPayload(listing_id=result.listing_id, status=result.status)

    @strawberry.mutation(description="Update mutable fields of an owned listing.")
    async def update_listing(
        self, info: Info, input: UpdateListingInput
    ) -> UpdateListingPayload:
        handler = UpdateListingHandler(
            info.context["uow_factory"](), info.context["event_publisher"]
        )
        try:
            result = await handler.handle(
                UpdateListingCommand(
                    listing_id=input.listing_id,
                    seller_id=input.seller_id,
                    title=input.title,
                    description=input.description,
                    price_amount=input.price_amount,
                    currency=input.currency,
                    quantity=input.quantity,
                    location=input.location,
                    category_id=input.category_id,
                )
            )
        except Exception as exc:
            raise_graphql_error(exc)
        return UpdateListingPayload(listing_id=result.listing_id, status=result.status)

    @strawberry.mutation(description="Delete an owned listing.")
    async def delete_listing(
        self, info: Info, input: DeleteListingInput
    ) -> DeleteListingPayload:
        handler = DeleteListingHandler(
            info.context["uow_factory"](), info.context["event_publisher"]
        )
        try:
            result = await handler.handle(
                DeleteListingCommand(
                    listing_id=input.listing_id, seller_id=input.seller_id
                )
            )
        except Exception as exc:
            raise_graphql_error(exc)
        return DeleteListingPayload(
            listing_id=result.listing_id, deleted=result.deleted
        )

    @strawberry.mutation(description="Publish a DRAFT listing (→ ACTIVE).")
    async def publish_listing(
        self, info: Info, input: PublishListingInput
    ) -> PublishListingPayload:
        handler = PublishListingHandler(
            info.context["uow_factory"](), info.context["event_publisher"]
        )
        try:
            result = await handler.handle(
                PublishListingCommand(
                    listing_id=input.listing_id, seller_id=input.seller_id
                )
            )
        except Exception as exc:
            raise_graphql_error(exc)
        return PublishListingPayload(listing_id=result.listing_id, status=result.status)

    @strawberry.mutation(description="Change listing status (sold, cancel, expire, …).")
    async def change_listing_status(
        self, info: Info, input: ChangeListingStatusInput
    ) -> ChangeListingStatusPayload:
        handler = ChangeListingStatusHandler(
            info.context["uow_factory"](), info.context["event_publisher"]
        )
        try:
            result = await handler.handle(
                ChangeListingStatusCommand(
                    listing_id=input.listing_id,
                    seller_id=input.seller_id,
                    new_status=input.new_status,
                )
            )
        except Exception as exc:
            raise_graphql_error(exc)
        return ChangeListingStatusPayload(
            listing_id=result.listing_id, status=result.status
        )

    @strawberry.mutation(description="Create a category in the taxonomy.")
    async def create_category(
        self, info: Info, input: CreateCategoryInput
    ) -> CreateCategoryPayload:
        handler = CreateCategoryHandler(
            info.context["uow_factory"](), info.context["event_publisher"]
        )
        try:
            result = await handler.handle(
                CreateCategoryCommand(name=input.name, parent_id=input.parent_id)
            )
        except Exception as exc:
            raise_graphql_error(exc)
        return CreateCategoryPayload(
            category_id=result.category_id,
            name=result.name,
            parent_id=result.parent_id,
            is_active=result.is_active,
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)
