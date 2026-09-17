import pytest
from src.application.verification_reset_password import (
    VerificationResetPassCommand,
    VerificationResetPassHandler,
)
from src.conf import Config
from src.domain.events.verification_token_created import VerificationTokenCreated
from src.exceptions import InvalidEmailError


@pytest.fixture
def handler(uow, token_repo, events) -> VerificationResetPassHandler:
    return VerificationResetPassHandler(
        uow=uow,
        token_repository=token_repo,
        event_publisher=events,
    )


class TestVerificationResetPassSuccess:
    async def test_stores_token_with_reset_ttl_when_user_exists(
        self, handler, uow, token_repo, make_user
    ):
        user = make_user(email="user@example.com")
        await uow.users.add(user)

        await handler.handle(VerificationResetPassCommand(email="user@example.com"))

        assert len(token_repo.added) == 1
        entry = token_repo.added[0]
        assert entry["email"] == "user@example.com"
        assert entry["token_type"] == "forget_pass_verify"
        assert entry["ttl_seconds"] == Config.RESET_PASSWORD_EXPIRE_MINUTES * 60

    async def test_publishes_verification_token_created(
        self, handler, uow, events, make_user
    ):
        user = make_user(email="user@example.com")
        await uow.users.add(user)

        await handler.handle(VerificationResetPassCommand(email="user@example.com"))

        assert len(events.published) == 1
        event = events.published[0]
        assert isinstance(event, VerificationTokenCreated)
        assert event.email == "user@example.com"
        assert event.token_type == "forget_pass_verify"

    async def test_email_is_normalized(self, handler, uow, token_repo, make_user):
        user = make_user(email="user@example.com")
        await uow.users.add(user)

        await handler.handle(VerificationResetPassCommand(email="  User@Example.COM  "))

        assert token_repo.added[0]["email"] == "user@example.com"


class TestVerificationResetPassSecurity:
    async def test_unknown_email_is_silent_noop(self, handler, token_repo, events):
        await handler.handle(VerificationResetPassCommand(email="ghost@example.com"))

        assert token_repo.added == []
        assert events.published == []

    async def test_registered_and_unregistered_return_same_shape(
        self, handler, uow, make_user
    ):
        user = make_user(email="user@example.com")
        await uow.users.add(user)

        registered = await handler.handle(
            VerificationResetPassCommand(email="user@example.com")
        )
        unregistered = await handler.handle(
            VerificationResetPassCommand(email="ghost@example.com")
        )

        assert registered is None
        assert unregistered is None


class TestVerificationResetPassFailures:
    async def test_invalid_email_rejected_before_lookup(self, handler, token_repo):
        with pytest.raises(InvalidEmailError):
            await handler.handle(VerificationResetPassCommand(email="not-an-email"))
        assert token_repo.added == []
