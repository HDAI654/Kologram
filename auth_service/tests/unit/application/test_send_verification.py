import pytest
from src.application.send_verification import (
    SendVerificationCommand,
    SendVerificationHandler,
)
from src.conf import Config
from src.domain.events.verification_token_created import VerificationTokenCreated
from src.exceptions import EmailBlockedError, InvalidEmailError


@pytest.fixture
def handler(token_repo, events, blocklist) -> SendVerificationHandler:
    return SendVerificationHandler(
        token_repository=token_repo,
        event_publisher=events,
        email_blocklist=blocklist,
    )


class TestSendVerificationSuccess:
    async def test_stores_token_with_configured_ttl(self, handler, token_repo):
        await handler.handle(SendVerificationCommand(email="user@example.com"))

        assert len(token_repo.added) == 1
        entry = token_repo.added[0]
        assert entry["email"] == "user@example.com"
        assert entry["token_type"] == "verifyemail"
        assert entry["ttl_seconds"] == Config.VERIFY_EMAIL_EXPIRE_MINUTES * 60

    async def test_publishes_token_created(self, handler, events):
        await handler.handle(SendVerificationCommand(email="user@example.com"))

        assert len(events.published) == 1
        event = events.published[0]
        assert isinstance(event, VerificationTokenCreated)
        assert event.email == "user@example.com"
        assert event.token_type == "verifyemail"

    async def test_email_is_normalized(self, handler, token_repo):
        await handler.handle(SendVerificationCommand(email="  User@Example.COM  "))

        assert token_repo.added[0]["email"] == "user@example.com"

    async def test_generated_tokens_are_unique(self, handler, token_repo):
        await handler.handle(SendVerificationCommand(email="a@example.com"))
        await handler.handle(SendVerificationCommand(email="a@example.com"))

        assert token_repo.added[0]["token"] != token_repo.added[1]["token"]


class TestSendVerificationFailures:
    async def test_blocked_email_raises_and_stores_nothing(self, token_repo, events):
        from tests.unit.application.conftest import FakeEmailBlocklistChecker

        checker = FakeEmailBlocklistChecker(blocked={"blocked@example.com"})
        handler = SendVerificationHandler(
            token_repository=token_repo,
            event_publisher=events,
            email_blocklist=checker,
        )

        with pytest.raises(EmailBlockedError):
            await handler.handle(SendVerificationCommand(email="blocked@example.com"))

        assert token_repo.added == []
        assert events.published == []

    async def test_invalid_email_rejected_before_blocklist_check(
        self, handler, token_repo, events
    ):
        with pytest.raises(InvalidEmailError):
            await handler.handle(SendVerificationCommand(email="not-an-email"))

        assert token_repo.added == []
        assert events.published == []
