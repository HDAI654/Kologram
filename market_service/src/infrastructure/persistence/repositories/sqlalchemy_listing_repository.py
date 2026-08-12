"""SQLAlchemy adapter for the ListingRepository port."""

from __future__ import annotations

import logging
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.listing import Listing
from src.domain.ports.listing_repository import ListingRepository
from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.user_id import UserId
from src.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
    ListingNotFoundError,
)
from src.infrastructure.persistence.mappers import listing_to_domain, listing_to_model
from src.infrastructure.persistence.models.listing import (
    ListingImageModel,
    ListingModel,
)

logger = logging.getLogger(__name__)


class SQLAlchemyListingRepository(ListingRepository):
    """Persist listing aggregates via SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, listing: Listing) -> None:
        logger.info(
            "Adding listing id=%s seller_id=%s",
            listing.id.value,
            listing.seller_id.value,
        )
        model = listing_to_model(listing)
        self._session.add(model)
        await self._execute_db_operation("add_listing", self._session.flush)
        logger.info("Listing added id=%s", listing.id.value)

    async def get_by_id(self, listing_id: ListingId) -> Listing:
        logger.info("Getting listing id=%s", listing_id.value)
        result = await self._execute_db_operation(
            "get_listing_by_id",
            self._session.execute,
            select(ListingModel)
            .options(selectinload(ListingModel.images))
            .where(ListingModel.id == listing_id.value),
        )
        model = result.scalar_one_or_none()
        if model is None:
            logger.debug("Listing not found id=%s", listing_id.value)
            raise ListingNotFoundError(f"Listing '{listing_id.value}' not found")
        logger.info("Listing found id=%s", listing_id.value)
        return listing_to_domain(model)

    async def update(self, listing: Listing) -> None:
        logger.info("Updating listing id=%s", listing.id.value)
        result = await self._execute_db_operation(
            "update_listing_load",
            self._session.execute,
            select(ListingModel)
            .options(selectinload(ListingModel.images))
            .where(ListingModel.id == listing.id.value),
        )
        model = result.scalar_one_or_none()
        if model is None:
            logger.debug("Listing not found for update id=%s", listing.id.value)
            raise ListingNotFoundError(f"Listing '{listing.id.value}' not found")

        model.seller_id = listing.seller_id.value
        model.category_id = listing.category_id.value
        model.title = listing.title.value
        model.description = listing.description.value
        model.price_amount = listing.price.amount
        model.currency = listing.price.currency
        model.quantity = listing.quantity.value
        model.status = listing.status.value
        model.location = listing.location.value
        model.updated_at = listing.updated_at

        model.images.clear()
        for img in listing.images:
            model.images.append(
                ListingImageModel(
                    id=img.id,
                    listing_id=listing.id.value,
                    url=img.url.value,
                    sort_order=img.sort_order.value,
                )
            )
        await self._execute_db_operation("update_listing", self._session.flush)
        logger.info("Listing updated id=%s", listing.id.value)

    async def delete(self, listing_id: ListingId) -> None:
        logger.info("Deleting listing id=%s", listing_id.value)
        result = await self._execute_db_operation(
            "delete_listing_load",
            self._session.execute,
            select(ListingModel).where(ListingModel.id == listing_id.value),
        )
        model = result.scalar_one_or_none()
        if model is None:
            logger.debug("Listing not found for delete id=%s", listing_id.value)
            raise ListingNotFoundError(f"Listing '{listing_id.value}' not found")
        await self._session.delete(model)
        await self._execute_db_operation("delete_listing", self._session.flush)
        logger.info("Listing deleted id=%s", listing_id.value)

    async def list_by_seller(
        self,
        seller_id: UserId,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Listing]:
        logger.info(
            "Listing listings by seller_id=%s limit=%s offset=%s",
            seller_id.value,
            limit,
            offset,
        )
        result = await self._execute_db_operation(
            "list_listings_by_seller",
            self._session.execute,
            select(ListingModel)
            .options(selectinload(ListingModel.images))
            .where(ListingModel.seller_id == seller_id.value)
            .order_by(ListingModel.created_at.desc())
            .limit(limit)
            .offset(offset),
        )
        items = [listing_to_domain(m) for m in result.scalars().all()]
        logger.info("Found %s listings for seller_id=%s", len(items), seller_id.value)
        return items

    async def search(
        self,
        *,
        query: str | None = None,
        category_id: str | None = None,
        status: str | None = None,
        seller_id: str | None = None,
        min_price: str | None = None,
        max_price: str | None = None,
        location: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Listing]:
        logger.info(
            "Searching listings query=%s category_id=%s status=%s",
            query,
            category_id,
            status,
        )
        stmt = select(ListingModel).options(selectinload(ListingModel.images))
        if query:
            pattern = f"%{query.strip()}%"
            stmt = stmt.where(
                or_(
                    ListingModel.title.ilike(pattern),
                    ListingModel.description.ilike(pattern),
                )
            )
        if category_id:
            stmt = stmt.where(ListingModel.category_id == category_id)
        if status:
            stmt = stmt.where(ListingModel.status == status.upper())
        if seller_id:
            stmt = stmt.where(ListingModel.seller_id == seller_id)
        if min_price is not None:
            stmt = stmt.where(ListingModel.price_amount >= Decimal(min_price))
        if max_price is not None:
            stmt = stmt.where(ListingModel.price_amount <= Decimal(max_price))
        if location:
            stmt = stmt.where(ListingModel.location.ilike(f"%{location.strip()}%"))
        stmt = stmt.order_by(ListingModel.created_at.desc()).limit(limit).offset(offset)
        result = await self._execute_db_operation(
            "search_listings", self._session.execute, stmt
        )
        items = [listing_to_domain(m) for m in result.scalars().all()]
        logger.info("Search returned %s listings", len(items))
        return items

    async def _execute_db_operation(self, operation: str, coro, *args, **kwargs):
        """Run a DB coroutine and map driver errors to infrastructure exceptions."""
        try:
            return await coro(*args, **kwargs)
        except IntegrityError as exc:
            logger.exception("Database integrity error during %s", operation)
            raise DatabaseOperationError(f"Database integrity error: {exc}") from exc
        except OperationalError as exc:
            logger.exception("Database connection error during %s", operation)
            raise DatabaseConnectionError(
                f"Failed to connect to database: {exc}"
            ) from exc
        except TimeoutError as exc:
            logger.exception("Database timeout during %s", operation)
            raise DatabaseTimeoutError(f"Database operation timed out: {exc}") from exc
        except SQLAlchemyError as exc:
            logger.exception("Database error during %s", operation)
            raise DatabaseOperationError(f"Database operation failed: {exc}") from exc
