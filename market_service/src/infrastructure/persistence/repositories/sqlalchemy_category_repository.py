"""SQLAlchemy adapter for the CategoryRepository port."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.category import Category
from src.domain.ports.category_repository import CategoryRepository
from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.category_name import CategoryName
from src.exceptions import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
)
from src.infrastructure.persistence.mappers import category_to_domain, category_to_model
from src.infrastructure.persistence.models.category import CategoryModel

logger = logging.getLogger(__name__)


class SQLAlchemyCategoryRepository(CategoryRepository):
    """Persist category aggregates via SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, category: Category) -> None:
        logger.info(
            "Adding category id=%s name=%s", category.id.value, category.name.value
        )
        model = category_to_model(category)
        self._session.add(model)
        await self._execute_db_operation("add_category", self._session.flush)
        logger.info("Category added id=%s", category.id.value)

    async def get_by_id(self, category_id: CategoryId) -> Category:
        logger.info("Getting category id=%s", category_id.value)
        result = await self._execute_db_operation(
            "get_category_by_id",
            self._session.execute,
            select(CategoryModel).where(CategoryModel.id == category_id.value),
        )
        model = result.scalar_one_or_none()
        if model is None:
            logger.debug("Category not found id=%s", category_id.value)
            raise CategoryNotFoundError(f"Category '{category_id.value}' not found")
        logger.info("Category found id=%s", category_id.value)
        return category_to_domain(model)

    async def get_by_name(self, name: CategoryName) -> Category | None:
        logger.info("Getting category by name=%s", name.value)
        result = await self._execute_db_operation(
            "get_category_by_name",
            self._session.execute,
            select(CategoryModel).where(CategoryModel.name == name.value),
        )
        model = result.scalar_one_or_none()
        if model is None:
            logger.debug("Category not found name=%s", name.value)
            return None
        logger.info("Category found name=%s", name.value)
        return category_to_domain(model)

    async def update(self, category: Category) -> None:
        logger.info("Updating category id=%s", category.id.value)
        result = await self._execute_db_operation(
            "update_category_load",
            self._session.execute,
            select(CategoryModel).where(CategoryModel.id == category.id.value),
        )
        model = result.scalar_one_or_none()
        if model is None:
            logger.debug("Category not found for update id=%s", category.id.value)
            raise CategoryNotFoundError(f"Category '{category.id.value}' not found")
        model.name = category.name.value
        model.parent_id = category.parent_id.value if category.parent_id else None
        model.is_active = category.is_active
        await self._execute_db_operation("update_category", self._session.flush)
        logger.info("Category updated id=%s", category.id.value)

    async def list_all(self, *, active_only: bool = False) -> list[Category]:
        logger.info("Listing categories active_only=%s", active_only)
        stmt = select(CategoryModel).order_by(CategoryModel.name)
        if active_only:
            stmt = stmt.where(CategoryModel.is_active.is_(True))
        result = await self._execute_db_operation(
            "list_categories", self._session.execute, stmt
        )
        items = [category_to_domain(m) for m in result.scalars().all()]
        logger.info("Found %s categories", len(items))
        return items

    async def list_children(self, parent_id: CategoryId) -> list[Category]:
        logger.info("Listing children of parent_id=%s", parent_id.value)
        result = await self._execute_db_operation(
            "list_category_children",
            self._session.execute,
            select(CategoryModel)
            .where(CategoryModel.parent_id == parent_id.value)
            .order_by(CategoryModel.name),
        )
        items = [category_to_domain(m) for m in result.scalars().all()]
        logger.info("Found %s child categories", len(items))
        return items

    async def _execute_db_operation(self, operation: str, coro, *args, **kwargs):
        """Run a DB coroutine and map driver errors to infrastructure exceptions."""
        try:
            return await coro(*args, **kwargs)
        except IntegrityError as exc:
            logger.exception("Database integrity error during %s", operation)
            if "duplicate" in str(exc).lower() or "unique" in str(exc).lower():
                raise CategoryAlreadyExistsError(
                    "Category with this name already exists"
                ) from exc
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
