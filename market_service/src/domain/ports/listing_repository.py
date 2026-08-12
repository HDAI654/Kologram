from abc import ABC, abstractmethod

from src.domain.entities.listing import Listing
from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.user_id import UserId


class ListingRepository(ABC):
    """Port for listing aggregate persistence."""

    @abstractmethod
    async def add(self, listing: Listing) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, listing_id: ListingId) -> Listing:
        raise NotImplementedError

    @abstractmethod
    async def update(self, listing: Listing) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, listing_id: ListingId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_seller(
        self,
        seller_id: UserId,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Listing]:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError
