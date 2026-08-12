from abc import ABC, abstractmethod
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword
from src.domain.value_objects.user_id import UserId


class UserRepository(ABC):
    """Port for user aggregate persistence."""

    @abstractmethod
    async def add(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: Email) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        user_id: UserId,
        *,
        new_password: HashedPassword | None = None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: UserId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_id(self, user_id: UserId) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        raise NotImplementedError
