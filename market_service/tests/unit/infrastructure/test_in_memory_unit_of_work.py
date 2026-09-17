from src.domain.value_objects.category_name import CategoryName
from src.infrastructure.persistence.in_memory_unit_of_work import (
    InMemoryUnitOfWork,
)


class TestLifecycle:
    async def test_context_manager_returns_self(self):
        uow = InMemoryUnitOfWork()
        async with uow as active:
            assert active is uow

    async def test_commit_is_noop(self):
        uow = InMemoryUnitOfWork()
        async with uow:
            await uow.commit()

    async def test_rollback_is_noop(self):
        uow = InMemoryUnitOfWork()
        async with uow:
            await uow.rollback()

    async def test_aexit_after_exception_does_not_raise(self):
        uow = InMemoryUnitOfWork()
        try:
            async with uow:
                raise RuntimeError("boom")
        except RuntimeError:
            pass


class TestStoreSharing:
    async def test_shared_stores_between_uows(self, make_category):
        store: dict = {}
        first = InMemoryUnitOfWork(categories=store)
        await first.categories.add(make_category(name="Electronics"))

        second = InMemoryUnitOfWork(categories=store)
        found = await second.categories.get_by_name(CategoryName("Electronics"))

        assert found is not None
        assert found.name.value == "Electronics"

    async def test_default_stores_are_isolated(self, make_category):
        a = InMemoryUnitOfWork()
        b = InMemoryUnitOfWork()
        await a.categories.add(make_category(name="Electronics"))

        assert await b.categories.get_by_name(CategoryName("Electronics")) is None

    async def test_shared_listing_stores_between_uows(self, make_listing):
        store: dict = {}
        first = InMemoryUnitOfWork(listings=store)
        listing = make_listing()
        await first.listings.add(listing)

        second = InMemoryUnitOfWork(listings=store)

        assert await second.listings.get_by_id(listing.id) is listing

    async def test_default_listing_stores_are_isolated(self, make_listing):
        from src.exceptions import ListingNotFoundError

        a = InMemoryUnitOfWork()
        b = InMemoryUnitOfWork()
        listing = make_listing()
        await a.listings.add(listing)

        try:
            await b.listings.get_by_id(listing.id)
        except ListingNotFoundError:
            pass
        else:
            raise AssertionError("expected ListingNotFoundError")
