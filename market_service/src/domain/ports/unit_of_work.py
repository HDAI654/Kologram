from abc import ABC, abstractmethod

from src.domain.ports.category_repository import CategoryRepository
from src.domain.ports.listing_repository import ListingRepository


class UnitOfWork(ABC):
    """Coordinates listing and category repository writes and transaction boundaries."""

    listings: ListingRepository
    categories: CategoryRepository

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
