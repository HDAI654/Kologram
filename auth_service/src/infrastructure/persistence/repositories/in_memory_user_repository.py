from src.domain.entities.user import User
from src.domain.ports.user_repository import UserRepository
from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword
from src.domain.value_objects.user_id import UserId
from src.exceptions import UserAlreadyExistsError, UserNotFoundError


class InMemoryUserRepository(UserRepository):
    """Process-local user store keyed by id and email."""

    def __init__(self) -> None:
        self._by_id: dict[str, User] = {}
        self._by_email: dict[str, str] = {}

    async def add(self, user: User) -> None:
        if user.email.value in self._by_email:
            raise UserAlreadyExistsError(
                f"User with email '{user.email.value}' already exists"
            )
        if user.id.value in self._by_id:
            raise UserAlreadyExistsError(
                f"User with id '{user.id.value}' already exists"
            )
        self._by_id[user.id.value] = user
        self._by_email[user.email.value] = user.id.value

    async def get_by_id(self, user_id: UserId) -> User:
        user = self._by_id.get(user_id.value)
        if user is None:
            raise UserNotFoundError(f"User '{user_id.value}' not found")
        return user

    async def get_by_email(self, email: Email) -> User:
        uid = self._by_email.get(email.value)
        if uid is None:
            raise UserNotFoundError(f"User with email '{email.value}' not found")
        return self._by_id[uid]

    async def update(
        self,
        user_id: UserId,
        *,
        new_password: HashedPassword | None = None,
    ) -> None:
        user = await self.get_by_id(user_id)
        if new_password is not None:
            user.change_password(new_password)

    async def delete(self, user_id: UserId) -> None:
        user = await self.get_by_id(user_id)
        del self._by_id[user.id.value]
        self._by_email.pop(user.email.value, None)

    async def exists_by_id(self, user_id: UserId) -> bool:
        return user_id.value in self._by_id

    async def exists_by_email(self, email: Email) -> bool:
        return email.value in self._by_email
