import pytest
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.category_name import CategoryName
from src.exceptions import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
)
from src.infrastructure.persistence.mappers import category_to_model
from src.infrastructure.persistence.models.category import CategoryModel
from src.infrastructure.persistence.repositories.sqlalchemy_category_repository import (
    SQLAlchemyCategoryRepository,
)

from tests.unit.infrastructure.conftest import (
    make_scalar_one_or_none_result,
    make_scalars_all_result,
)


class TestAdd:
    async def test_add_flushes_without_committing(self, session, make_category):
        repo = SQLAlchemyCategoryRepository(session)

        await repo.add(make_category())

        session.add.assert_called_once()
        session.flush.assert_awaited_once()
        session.commit.assert_not_awaited()

    async def test_add_maps_domain_to_model(self, session, make_category):
        repo = SQLAlchemyCategoryRepository(session)
        category = make_category(name="Electronics")

        await repo.add(category)

        model = session.add.call_args.args[0]
        assert isinstance(model, CategoryModel)
        assert model.id == category.id.value
        assert model.name == "Electronics"

    async def test_add_translates_duplicate_integrity_error(
        self, session, make_category
    ):
        session.flush.side_effect = IntegrityError(
            "stmt", {}, Exception("duplicate key value")
        )
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(CategoryAlreadyExistsError):
            await repo.add(make_category())

    async def test_add_translates_unique_integrity_error(self, session, make_category):
        session.flush.side_effect = IntegrityError(
            "stmt", {}, Exception("UNIQUE constraint failed")
        )
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(CategoryAlreadyExistsError):
            await repo.add(make_category())

    async def test_add_translates_non_duplicate_integrity_error_to_operation_error(
        self, session, make_category
    ):
        session.flush.side_effect = IntegrityError(
            "stmt", {}, Exception("foreign key violation")
        )
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(DatabaseOperationError):
            await repo.add(make_category())

    async def test_add_translates_operational_error(self, session, make_category):
        session.flush.side_effect = OperationalError("stmt", {}, Exception("down"))
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(DatabaseConnectionError):
            await repo.add(make_category())

    async def test_add_translates_timeout_error(self, session, make_category):
        session.flush.side_effect = TimeoutError("slow")
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(DatabaseTimeoutError):
            await repo.add(make_category())

    async def test_add_translates_generic_sqlalchemy_error(
        self, session, make_category
    ):
        session.flush.side_effect = SQLAlchemyError("bad")
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(DatabaseOperationError):
            await repo.add(make_category())

    async def test_add_preserves_cause_on_translation(self, session, make_category):
        underlying = OperationalError("stmt", {}, Exception("down"))
        session.flush.side_effect = underlying
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(DatabaseConnectionError) as exc_info:
            await repo.add(make_category())

        assert exc_info.value.__cause__ is underlying


class TestGetById:
    async def test_get_by_id_returns_domain_when_found(self, session, make_category):
        category = make_category(name="Electronics")
        session.execute.return_value = make_scalar_one_or_none_result(
            category_to_model(category)
        )
        repo = SQLAlchemyCategoryRepository(session)

        result = await repo.get_by_id(category.id)

        assert result.id == category.id
        assert result.name.value == "Electronics"
        session.commit.assert_not_awaited()

    async def test_get_by_id_raises_not_found(self, session):
        session.execute.return_value = make_scalar_one_or_none_result(None)
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(CategoryNotFoundError):
            await repo.get_by_id(CategoryId.generate())

    async def test_get_by_id_translates_operational_error(self, session):
        session.execute.side_effect = OperationalError("stmt", {}, Exception("down"))
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(DatabaseConnectionError):
            await repo.get_by_id(CategoryId.generate())

    async def test_get_by_id_translates_timeout_error(self, session):
        session.execute.side_effect = TimeoutError("slow")
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(DatabaseTimeoutError):
            await repo.get_by_id(CategoryId.generate())

    async def test_get_by_id_translates_generic_sqlalchemy_error(self, session):
        session.execute.side_effect = SQLAlchemyError("bad")
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(DatabaseOperationError):
            await repo.get_by_id(CategoryId.generate())


class TestGetByName:
    async def test_get_by_name_returns_domain_when_found(self, session, make_category):
        category = make_category(name="Electronics")
        session.execute.return_value = make_scalar_one_or_none_result(
            category_to_model(category)
        )
        repo = SQLAlchemyCategoryRepository(session)

        result = await repo.get_by_name(CategoryName("Electronics"))

        assert result is not None
        assert result.name.value == "Electronics"

    async def test_get_by_name_returns_none_when_missing(self, session):
        session.execute.return_value = make_scalar_one_or_none_result(None)
        repo = SQLAlchemyCategoryRepository(session)

        assert await repo.get_by_name(CategoryName("Electronics")) is None

    async def test_get_by_name_translates_operational_error(self, session):
        session.execute.side_effect = OperationalError("stmt", {}, Exception("down"))
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(DatabaseConnectionError):
            await repo.get_by_name(CategoryName("Electronics"))


class TestUpdate:
    async def test_update_flushes_without_committing(self, session, make_category):
        category = make_category(name="Electronics")
        model = category_to_model(category)
        session.execute.return_value = make_scalar_one_or_none_result(model)
        repo = SQLAlchemyCategoryRepository(session)

        category.rename("Consumer Electronics")
        await repo.update(category)

        assert model.name == "Consumer Electronics"
        session.flush.assert_awaited_once()
        session.commit.assert_not_awaited()

    async def test_update_raises_not_found_when_missing(self, session, make_category):
        session.execute.return_value = make_scalar_one_or_none_result(None)
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(CategoryNotFoundError):
            await repo.update(make_category())

    async def test_update_clears_parent_when_none(self, session, make_category):
        parent = make_category(name="Root Category")
        child = make_category(name="Leaf Category", parent_id=parent.id.value)
        model = category_to_model(child)
        session.execute.return_value = make_scalar_one_or_none_result(model)
        repo = SQLAlchemyCategoryRepository(session)

        child.parent_id = None
        await repo.update(child)

        assert model.parent_id is None

    async def test_update_translates_operational_error(self, session, make_category):
        session.execute.side_effect = OperationalError("stmt", {}, Exception("down"))
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(DatabaseConnectionError):
            await repo.update(make_category())


class TestListAll:
    async def test_list_all_returns_all(self, session, make_category):
        items = [
            category_to_model(make_category(name="Alpha")),
            category_to_model(make_category(name="Beta")),
        ]
        session.execute.return_value = make_scalars_all_result(items)
        repo = SQLAlchemyCategoryRepository(session)

        result = await repo.list_all()

        assert [c.name.value for c in result] == ["Alpha", "Beta"]

    async def test_list_all_active_only_uses_scalars(self, session, make_category):
        items = [category_to_model(make_category(name="Alpha"))]
        session.execute.return_value = make_scalars_all_result(items)
        repo = SQLAlchemyCategoryRepository(session)

        result = await repo.list_all(active_only=True)

        assert len(result) == 1
        assert result[0].name.value == "Alpha"

    async def test_list_all_empty(self, session):
        session.execute.return_value = make_scalars_all_result([])
        repo = SQLAlchemyCategoryRepository(session)

        assert await repo.list_all() == []

    async def test_list_all_translates_operational_error(self, session):
        session.execute.side_effect = OperationalError("stmt", {}, Exception("down"))
        repo = SQLAlchemyCategoryRepository(session)

        with pytest.raises(DatabaseConnectionError):
            await repo.list_all()


class TestListChildren:
    async def test_list_children_filters_by_parent(self, session, make_category):
        parent = make_category(name="Root Category")
        child_model = category_to_model(
            make_category(name="Leaf Category", parent_id=parent.id.value)
        )
        session.execute.return_value = make_scalars_all_result([child_model])
        repo = SQLAlchemyCategoryRepository(session)

        result = await repo.list_children(parent.id)

        assert len(result) == 1
        assert result[0].parent_id == parent.id

    async def test_list_children_empty(self, session):
        session.execute.return_value = make_scalars_all_result([])
        repo = SQLAlchemyCategoryRepository(session)

        assert await repo.list_children(CategoryId.generate()) == []
