from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.user_id import UserId
from src.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
    ListingNotFoundError,
)
from src.infrastructure.persistence.mappers import listing_to_model
from src.infrastructure.persistence.models.listing import ListingModel
from src.infrastructure.persistence.repositories.sqlalchemy_listing_repository import (
    SQLAlchemyListingRepository,
)

from tests.unit.infrastructure.conftest import (
    make_scalar_one_or_none_result,
    make_scalars_all_result,
)


class TestAdd:
    async def test_add_flushes_without_committing(self, session, make_listing):
        repo = SQLAlchemyListingRepository(session)

        await repo.add(make_listing())

        session.add.assert_called_once()
        session.flush.assert_awaited_once()
        session.commit.assert_not_awaited()

    async def test_add_maps_domain_to_model(self, session, make_listing):
        repo = SQLAlchemyListingRepository(session)
        listing = make_listing(title="Vintage Camera")

        await repo.add(listing)

        model = session.add.call_args.args[0]
        assert isinstance(model, ListingModel)
        assert model.title == "Vintage Camera"
        assert model.seller_id == listing.seller_id.value

    async def test_add_translates_integrity_error_to_operation_error(
        self, session, make_listing
    ):
        session.flush.side_effect = IntegrityError("stmt", {}, Exception("fk"))
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseOperationError):
            await repo.add(make_listing())

    async def test_add_translates_operational_error(self, session, make_listing):
        session.flush.side_effect = OperationalError("stmt", {}, Exception("down"))
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseConnectionError):
            await repo.add(make_listing())

    async def test_add_translates_timeout_error(self, session, make_listing):
        session.flush.side_effect = TimeoutError("slow")
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseTimeoutError):
            await repo.add(make_listing())

    async def test_add_preserves_cause_on_translation(self, session, make_listing):
        underlying = OperationalError("stmt", {}, Exception("down"))
        session.flush.side_effect = underlying
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseConnectionError) as exc_info:
            await repo.add(make_listing())

        assert exc_info.value.__cause__ is underlying


class TestGetById:
    async def test_returns_domain_when_found(self, session, make_listing):
        listing = make_listing()
        session.execute.return_value = make_scalar_one_or_none_result(
            listing_to_model(listing)
        )
        repo = SQLAlchemyListingRepository(session)

        result = await repo.get_by_id(listing.id)

        assert result.id == listing.id
        assert result.title == listing.title
        session.commit.assert_not_awaited()

    async def test_raises_not_found_when_missing(self, session):
        session.execute.return_value = make_scalar_one_or_none_result(None)
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(ListingNotFoundError):
            await repo.get_by_id(ListingId.generate())

    async def test_translates_operational_error(self, session):
        session.execute.side_effect = OperationalError("stmt", {}, Exception("down"))
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseConnectionError):
            await repo.get_by_id(ListingId.generate())

    async def test_translates_timeout_error(self, session):
        session.execute.side_effect = TimeoutError("slow")
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseTimeoutError):
            await repo.get_by_id(ListingId.generate())

    async def test_translates_generic_sqlalchemy_error(self, session):
        session.execute.side_effect = SQLAlchemyError("bad")
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseOperationError):
            await repo.get_by_id(ListingId.generate())


class TestUpdate:
    async def test_update_flushes_without_committing(self, session, make_listing):
        listing = make_listing()
        model = listing_to_model(listing)
        session.execute.return_value = make_scalar_one_or_none_result(model)
        repo = SQLAlchemyListingRepository(session)

        listing.update_details(title="Updated Title")
        await repo.update(listing)

        assert model.title == "Updated Title"
        session.flush.assert_awaited_once()
        session.commit.assert_not_awaited()

    async def test_update_replaces_images(self, session, make_listing):
        listing = make_listing()
        model = listing_to_model(listing)
        session.execute.return_value = make_scalar_one_or_none_result(model)
        repo = SQLAlchemyListingRepository(session)

        listing.add_image(url="https://example.com/new.jpg", sort_order=0)
        await repo.update(listing)

        assert len(model.images) == 1
        assert model.images[0].url == "https://example.com/new.jpg"

    async def test_update_raises_not_found(self, session, make_listing):
        session.execute.return_value = make_scalar_one_or_none_result(None)
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(ListingNotFoundError):
            await repo.update(make_listing())

    async def test_update_translates_operational_error(self, session, make_listing):
        session.execute.side_effect = OperationalError("stmt", {}, Exception("down"))
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseConnectionError):
            await repo.update(make_listing())


class TestDelete:
    async def test_delete_flushes_without_committing(self, session, make_listing):
        listing = make_listing()
        model = listing_to_model(listing)
        session.execute.return_value = make_scalar_one_or_none_result(model)
        repo = SQLAlchemyListingRepository(session)

        await repo.delete(listing.id)

        session.delete.assert_awaited_once_with(model)
        session.flush.assert_awaited_once()
        session.commit.assert_not_awaited()

    async def test_delete_raises_not_found(self, session):
        session.execute.return_value = make_scalar_one_or_none_result(None)
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(ListingNotFoundError):
            await repo.delete(ListingId.generate())

    async def test_delete_translates_operational_error_from_flush(
        self, session, make_listing
    ):
        # ``session.delete`` is not wrapped by the repository; ``flush`` is.
        listing = make_listing()
        session.execute.return_value = make_scalar_one_or_none_result(
            listing_to_model(listing)
        )
        session.flush.side_effect = OperationalError("stmt", {}, Exception("down"))
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseConnectionError):
            await repo.delete(listing.id)

    async def test_delete_translates_generic_sqlalchemy_error_from_flush(
        self, session, make_listing
    ):
        listing = make_listing()
        session.execute.return_value = make_scalar_one_or_none_result(
            listing_to_model(listing)
        )
        session.flush.side_effect = SQLAlchemyError("bad")
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseOperationError):
            await repo.delete(listing.id)


class TestListBySeller:
    async def test_returns_listings_for_seller(self, session, make_listing):
        seller_id = UserId.generate()
        items = [
            listing_to_model(make_listing(seller_id=seller_id.value)),
            listing_to_model(make_listing(seller_id=seller_id.value)),
        ]
        session.execute.return_value = make_scalars_all_result(items)
        repo = SQLAlchemyListingRepository(session)

        result = await repo.list_by_seller(seller_id, limit=10, offset=0)

        assert len(result) == 2
        assert all(lst.seller_id == seller_id for lst in result)

    async def test_empty_result(self, session):
        session.execute.return_value = make_scalars_all_result([])
        repo = SQLAlchemyListingRepository(session)

        assert await repo.list_by_seller(UserId.generate()) == []

    async def test_translates_operational_error(self, session):
        session.execute.side_effect = OperationalError("stmt", {}, Exception("down"))
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseConnectionError):
            await repo.list_by_seller(UserId.generate())


class TestSearch:
    async def test_search_returns_snapshots(self, session, make_listing):
        items = [listing_to_model(make_listing(status="ACTIVE"))]
        session.execute.return_value = make_scalars_all_result(items)
        repo = SQLAlchemyListingRepository(session)

        result = await repo.search(query="camera", status="ACTIVE")

        assert len(result) == 1

    async def test_search_applies_price_range(self, session, make_listing):
        items = [listing_to_model(make_listing(price_amount="50.00"))]
        session.execute.return_value = make_scalars_all_result(items)
        repo = SQLAlchemyListingRepository(session)

        result = await repo.search(min_price="10.00", max_price="100.00")

        assert len(result) == 1
        assert result[0].price.amount == Decimal("50.00")

    async def test_search_with_no_filters_returns_all(self, session, make_listing):
        items = [listing_to_model(make_listing())]
        session.execute.return_value = make_scalars_all_result(items)
        repo = SQLAlchemyListingRepository(session)

        assert len(await repo.search()) == 1

    async def test_search_translates_operational_error(self, session):
        session.execute.side_effect = OperationalError("stmt", {}, Exception("down"))
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseConnectionError):
            await repo.search()

    async def test_search_translates_generic_sqlalchemy_error(self, session):
        session.execute.side_effect = SQLAlchemyError("bad")
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseOperationError):
            await repo.search()

    async def test_search_translates_timeout_error(self, session):
        session.execute.side_effect = TimeoutError("slow")
        repo = SQLAlchemyListingRepository(session)

        with pytest.raises(DatabaseTimeoutError):
            await repo.search()
