import pytest
from src.application.login import LoginCommand, LoginHandler
from src.domain.events.user_logged_in import UserLoggedIn
from src.exceptions import (
    AccountSuspendedError,
    InvalidDeviceError,
    InvalidEmailError,
    InvalidEmailOrPasswordError,
)


@pytest.fixture
def handler(uow, session_repo, encoder, hasher, events) -> LoginHandler:
    return LoginHandler(
        uow=uow,
        session_repository=session_repo,
        token_encoder=encoder,
        password_hasher=hasher,
        event_publisher=events,
    )


class TestLoginSuccess:
    async def test_issues_access_and_refresh_tokens(self, handler, uow, make_user):
        user = make_user()
        await uow.users.add(user)

        result = await handler.handle(
            LoginCommand(
                email="user@example.com", password="password1", device="iPhone"
            )
        )

        assert result.access_token.startswith(f"access::{user.id.value}")
        assert result.refresh_token.startswith(f"refresh::{user.id.value}")

    async def test_creates_session_with_device(
        self, handler, uow, session_repo, make_user
    ):
        user = make_user()
        await uow.users.add(user)

        await handler.handle(
            LoginCommand(
                email="user@example.com", password="password1", device="Pixel 8"
            )
        )

        assert len(session_repo.added) == 1
        assert session_repo.added[0].user_id == user.id
        assert session_repo.added[0].device.value == "Pixel 8"

    async def test_publishes_user_logged_in(self, handler, uow, events, make_user):
        user = make_user()
        await uow.users.add(user)

        await handler.handle(
            LoginCommand(
                email="user@example.com", password="password1", device="iPhone"
            )
        )

        assert len(events.published) == 1
        event = events.published[0]
        assert isinstance(event, UserLoggedIn)
        assert event.user_id == user.id.value
        assert event.email == user.email.value
        assert event.device == "iPhone"

    async def test_email_is_normalized_before_lookup(self, handler, uow, make_user):
        user = make_user(email="user@example.com")
        await uow.users.add(user)

        # Different case + whitespace still resolves.
        await handler.handle(
            LoginCommand(
                email="  User@Example.COM  ", password="password1", device="iPhone"
            )
        )

    async def test_no_publisher_still_issues_tokens(
        self, uow, session_repo, encoder, hasher, make_user
    ):
        user = make_user()
        await uow.users.add(user)
        handler = LoginHandler(
            uow=uow,
            session_repository=session_repo,
            token_encoder=encoder,
            password_hasher=hasher,
            event_publisher=None,
        )

        result = await handler.handle(
            LoginCommand(
                email="user@example.com", password="password1", device="iPhone"
            )
        )
        assert result.access_token


class TestLoginSecurity:
    async def test_unknown_email_and_wrong_password_share_same_exception(
        self, handler, uow, hasher, make_user
    ):
        user = make_user()
        await uow.users.add(user)
        hasher.verify_result = False

        wrong_password: Exception | None = None
        try:
            await handler.handle(
                LoginCommand(
                    email="user@example.com", password="wrongpass1", device="iPhone"
                )
            )
        except Exception as exc:  # noqa: BLE001
            wrong_password = exc

        unknown: Exception | None = None
        try:
            await handler.handle(
                LoginCommand(
                    email="ghost@example.com", password="password1", device="iPhone"
                )
            )
        except Exception as exc:  # noqa: BLE001
            unknown = exc

        assert type(wrong_password) is type(unknown)
        assert isinstance(wrong_password, InvalidEmailOrPasswordError)


class TestLoginFailures:
    async def test_unknown_email_raises_generic_error(self, handler, session_repo):
        with pytest.raises(InvalidEmailOrPasswordError):
            await handler.handle(
                LoginCommand(
                    email="ghost@example.com", password="password1", device="iPhone"
                )
            )
        assert session_repo.added == []

    async def test_wrong_password_raises_generic_error(
        self, handler, uow, session_repo, hasher, make_user
    ):
        user = make_user()
        await uow.users.add(user)
        hasher.verify_result = False

        with pytest.raises(InvalidEmailOrPasswordError):
            await handler.handle(
                LoginCommand(
                    email="user@example.com", password="wrongpass1", device="iPhone"
                )
            )
        assert session_repo.added == []

    async def test_malformed_email_raises_domain_error(self, handler):
        with pytest.raises(InvalidEmailError):
            await handler.handle(
                LoginCommand(
                    email="not-an-email", password="password1", device="iPhone"
                )
            )

    async def test_invalid_device_rejected_after_credentials_verified(
        self, handler, uow, session_repo, make_user
    ):
        user = make_user()
        await uow.users.add(user)

        with pytest.raises(InvalidDeviceError):
            await handler.handle(
                LoginCommand(email="user@example.com", password="password1", device="")
            )
        assert session_repo.added == []

    async def test_no_event_on_failure(self, handler, uow, events, hasher, make_user):
        user = make_user()
        await uow.users.add(user)
        hasher.verify_result = False

        with pytest.raises(InvalidEmailOrPasswordError):
            await handler.handle(
                LoginCommand(
                    email="user@example.com", password="x1xxxxxx", device="iPhone"
                )
            )
        assert events.published == []


class TestLoginTransaction:
    async def test_read_only_no_commit(self, handler, uow, make_user):
        user = make_user()
        await uow.users.add(user)

        await handler.handle(
            LoginCommand(
                email="user@example.com", password="password1", device="iPhone"
            )
        )

        assert uow.committed is False
