import logging
from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
    TimeoutError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.ports.user_repository import UserRepository
from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword
from src.domain.value_objects.user_id import UserId
from src.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.infrastructure.persistence.mappers import model_to_user, user_to_model
from src.infrastructure.persistence.models.user import UserModel

logger = logging.getLogger(__name__)


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: User) -> None:
        model = user_to_model(user)
        self._session.add(model)
        try:
            await self._execute_db_operation("add_user", self._session.flush)
        except DatabaseOperationError as exc:
            # Unique email violation → domain conflict
            if "unique" in str(exc).lower() or "integrity" in str(exc).lower():
                raise UserAlreadyExistsError(
                    f"User with email '{user.email.value}' already exists"
                ) from exc
            raise

    async def get_by_id(self, user_id: UserId) -> User:
        result = await self._execute_db_operation(
            "get_by_id",
            self._session.execute,
            select(UserModel).where(UserModel.id == user_id.value),
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise UserNotFoundError(f"User '{user_id.value}' not found")
        return model_to_user(model)

    async def get_by_email(self, email: Email) -> User:
        result = await self._execute_db_operation(
            "get_by_email",
            self._session.execute,
            select(UserModel).where(UserModel.email == email.value),
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise UserNotFoundError(f"User with email '{email.value}' not found")
        return model_to_user(model)

    async def update(
        self,
        user_id: UserId,
        *,
        new_password: HashedPassword | None = None,
    ) -> None:
        result = await self._execute_db_operation(
            "update_get",
            self._session.execute,
            select(UserModel).where(UserModel.id == user_id.value),
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise UserNotFoundError(f"User '{user_id.value}' not found")
        if new_password is not None:
            model.hashed_password = new_password.value
        await self._execute_db_operation("update_flush", self._session.flush)

    async def delete(self, user_id: UserId) -> None:
        result = await self._execute_db_operation(
            "delete_get",
            self._session.execute,
            select(UserModel).where(UserModel.id == user_id.value),
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise UserNotFoundError(f"User '{user_id.value}' not found")
        await self._execute_db_operation("delete_user", self._session.delete, model)
        await self._execute_db_operation("delete_flush", self._session.flush)

    async def exists_by_id(self, user_id: UserId) -> bool:
        result = await self._execute_db_operation(
            "exists_by_id",
            self._session.execute,
            select(UserModel.id).where(UserModel.id == user_id.value),
        )
        return result.scalar_one_or_none() is not None

    async def exists_by_email(self, email: Email) -> bool:
        result = await self._execute_db_operation(
            "exists_by_email",
            self._session.execute,
            select(UserModel.id).where(UserModel.email == email.value),
        )
        return result.scalar_one_or_none() is not None

    async def _execute_db_operation(self, operation: str, coro, *args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except IntegrityError as e:
            logger.exception("Database integrity error during %s", operation)
            raise DatabaseOperationError(f"Database integrity error: {e}") from e
        except OperationalError as e:
            logger.exception("Database connection error during %s", operation)
            raise DatabaseConnectionError(f"Failed to connect to database: {e}") from e
        except TimeoutError as e:
            logger.exception("Database timeout during %s", operation)
            raise DatabaseTimeoutError(f"Database operation timed out: {e}") from e
        except SQLAlchemyError as e:
            logger.exception("Database error during %s", operation)
            raise DatabaseOperationError(f"Database operation failed: {e}") from e
