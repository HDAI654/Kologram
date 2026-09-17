import pytest
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
    TimeoutError,
)

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
from src.infrastructure.persistence.mappers import user_to_model
from src.infrastructure.persistence.models.user import UserModel
from src.infrastructure.persistence.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

from tests.unit.infrastructure.conftest import scalar_one_or_none


class TestAdd:
    async def test_flushes_without_committing(self, session, make_user):
        repo = SQLAlchemyUserRepository(session)
        await repo.add(make_user())
        session.add.assert_called_once()
        session.flush.assert_awaited_once()
        session.commit.assert_not_awaited()

    async def test_maps_domain_to_model(self, session, make_user):
        repo = SQLAlchemyUserRepository(session)
        user = make_user(email="user@example.com")
        await repo.add(user)
        model = session.add.call_args.args[0]
        assert isinstance(model, UserModel)
        assert model.email == "user@example.com"

    async def test_unique_integrity_error_becomes_domain_conflict(
        self, session, make_user
    ):
        session.flush.side_effect = IntegrityError(
            "stmt", {}, Exception("unique constraint violated")
        )
        repo = SQLAlchemyUserRepository(session)
        with pytest.raises(UserAlreadyExistsError):
            await repo.add(make_user())

    async def test_non_unique_integrity_error_becomes_operation_error(
        self, session, make_user
    ):
        session.flush.side_effect = IntegrityError("stmt", {}, Exception("fk failure"))
        repo = SQLAlchemyUserRepository(session)
        with pytest.raises(DatabaseOperationError):
            await repo.add(make_user())

    async def test_operational_error_becomes_connection_error(self, session, make_user):
        session.flush.side_effect = OperationalError("stmt", {}, Exception("down"))
        repo = SQLAlchemyUserRepository(session)
        with pytest.raises(DatabaseConnectionError):
            await repo.add(make_user())

    async def test_timeout_becomes_timeout_error(self, session, make_user):
        session.flush.side_effect = TimeoutError("slow")
        repo = SQLAlchemyUserRepository(session)
        with pytest.raises(DatabaseTimeoutError):
            await repo.add(make_user())

    async def test_generic_sqlalchemy_error_becomes_operation_error(
        self, session, make_user
    ):
        session.flush.side_effect = SQLAlchemyError("bad")
        repo = SQLAlchemyUserRepository(session)
        with pytest.raises(DatabaseOperationError):
            await repo.add(make_user())


class TestGetById:
    async def test_returns_domain_user(self, session, make_user):
        user = make_user()
        session.execute.return_value = scalar_one_or_none(user_to_model(user))
        repo = SQLAlchemyUserRepository(session)
        result = await repo.get_by_id(user.id)
        assert result.id == user.id
        assert result.email == user.email
        session.commit.assert_not_awaited()

    async def test_missing_raises(self, session):
        session.execute.return_value = scalar_one_or_none(None)
        repo = SQLAlchemyUserRepository(session)
        with pytest.raises(UserNotFoundError):
            await repo.get_by_id(UserId.generate())

    async def test_operational_error_translated(self, session):
        session.execute.side_effect = OperationalError("stmt", {}, Exception("down"))
        repo = SQLAlchemyUserRepository(session)
        with pytest.raises(DatabaseConnectionError):
            await repo.get_by_id(UserId.generate())


class TestGetByEmail:
    async def test_returns_domain_user(self, session, make_user):
        user = make_user(email="user@example.com")
        session.execute.return_value = scalar_one_or_none(user_to_model(user))
        repo = SQLAlchemyUserRepository(session)
        result = await repo.get_by_email(Email("user@example.com"))
        assert result.email == user.email

    async def test_missing_raises(self, session):
        session.execute.return_value = scalar_one_or_none(None)
        repo = SQLAlchemyUserRepository(session)
        with pytest.raises(UserNotFoundError):
            await repo.get_by_email(Email("ghost@example.com"))


class TestUpdate:
    async def test_flushes_new_password(self, session, make_user):
        user = make_user()
        model = user_to_model(user)
        session.execute.return_value = scalar_one_or_none(model)
        repo = SQLAlchemyUserRepository(session)

        await repo.update(user.id, new_password=HashedPassword("$2b$12$new"))

        assert model.hashed_password == "$2b$12$new"
        session.flush.assert_awaited_once()
        session.commit.assert_not_awaited()

    async def test_noop_when_password_is_none(self, session, make_user):
        user = make_user()
        model = user_to_model(user)
        original = model.hashed_password
        session.execute.return_value = scalar_one_or_none(model)
        repo = SQLAlchemyUserRepository(session)

        await repo.update(user.id, new_password=None)

        assert model.hashed_password == original

    async def test_missing_raises(self, session):
        session.execute.return_value = scalar_one_or_none(None)
        repo = SQLAlchemyUserRepository(session)
        with pytest.raises(UserNotFoundError):
            await repo.update(
                UserId.generate(), new_password=HashedPassword("$2b$12$x")
            )


class TestDelete:
    async def test_delegates_session_delete_and_flush(self, session, make_user):
        user = make_user()
        model = user_to_model(user)
        session.execute.return_value = scalar_one_or_none(model)
        repo = SQLAlchemyUserRepository(session)

        await repo.delete(user.id)

        session.delete.assert_awaited_once_with(model)
        session.flush.assert_awaited_once()
        session.commit.assert_not_awaited()

    async def test_missing_raises(self, session):
        session.execute.return_value = scalar_one_or_none(None)
        repo = SQLAlchemyUserRepository(session)
        with pytest.raises(UserNotFoundError):
            await repo.delete(UserId.generate())


class TestExists:
    async def test_exists_by_id_true(self, session):
        session.execute.return_value = scalar_one_or_none("some-id")
        repo = SQLAlchemyUserRepository(session)
        assert await repo.exists_by_id(UserId.generate()) is True

    async def test_exists_by_id_false(self, session):
        session.execute.return_value = scalar_one_or_none(None)
        repo = SQLAlchemyUserRepository(session)
        assert await repo.exists_by_id(UserId.generate()) is False

    async def test_exists_by_email_true(self, session):
        session.execute.return_value = scalar_one_or_none("some-id")
        repo = SQLAlchemyUserRepository(session)
        assert await repo.exists_by_email(Email("user@example.com")) is True

    async def test_exists_by_email_false(self, session):
        session.execute.return_value = scalar_one_or_none(None)
        repo = SQLAlchemyUserRepository(session)
        assert await repo.exists_by_email(Email("ghost@example.com")) is False
