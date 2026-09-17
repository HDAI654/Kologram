import pytest
from src.application.signup import SignupCommand, SignupHandler
from src.domain.events.user_registered import UserRegistered
from src.domain.value_objects.email import Email
from src.domain.value_objects.verification_token import VerificationToken
from src.exceptions import (
    InvalidPasswordError,
    InvalidVerificationTokenError,
)


@pytest.fixture
def handler(uow, session_repo, encoder, hasher, token_repo, events) -> SignupHandler:
    return SignupHandler(
        uow=uow,
        session_repository=session_repo,
        token_encoder=encoder,
        password_hasher=hasher,
        token_repository=token_repo,
        event_publisher=events,
    )


async def _store_verify_token(token_repo, email: str) -> VerificationToken:
    token = VerificationToken.generate()
    await token_repo.add(
        token=token,
        email=Email(email),
        token_type="verifyemail",
        ttl_seconds=3600,
    )
    return token


class TestSignupSuccess:
    async def test_creates_user_and_commits(self, handler, uow, token_repo):
        token = await _store_verify_token(token_repo, "user@example.com")

        await handler.handle(
            SignupCommand(
                verify_token=token.value, password="password1", device="iPhone"
            )
        )

        assert uow.committed is True
        assert len(uow.users.added) == 1
        user = uow.users.added[0]
        assert user.email.value == "user@example.com"
        assert user.hashed_password.value == "hashed::password1"

    async def test_creates_session_and_issues_tokens(
        self, handler, uow, session_repo, token_repo
    ):
        token = await _store_verify_token(token_repo, "user@example.com")

        result = await handler.handle(
            SignupCommand(
                verify_token=token.value, password="password1", device="iPhone"
            )
        )

        assert len(session_repo.added) == 1
        session = session_repo.added[0]
        assert session.device.value == "iPhone"
        assert result.access_token.startswith(f"access::{session.user_id.value}")
        assert result.refresh_token.startswith(f"refresh::{session.user_id.value}")

    async def test_consumes_token_after_commit(self, handler, uow, token_repo):
        token = await _store_verify_token(token_repo, "user@example.com")

        await handler.handle(
            SignupCommand(
                verify_token=token.value, password="password1", device="iPhone"
            )
        )

        assert ("verifyemail", token.value) in token_repo.deleted

    async def test_publishes_user_registered(self, handler, uow, token_repo, events):
        token = await _store_verify_token(token_repo, "user@example.com")

        await handler.handle(
            SignupCommand(
                verify_token=token.value, password="password1", device="iPhone"
            )
        )

        assert len(events.published) == 1
        event = events.published[0]
        assert isinstance(event, UserRegistered)
        assert event.email == "user@example.com"

    async def test_email_is_normalized(self, handler, uow, token_repo):
        token = await _store_verify_token(token_repo, "USER@Example.COM")

        await handler.handle(
            SignupCommand(
                verify_token=token.value, password="password1", device="iPhone"
            )
        )

        assert uow.users.added[0].email.value == "user@example.com"


class TestSignupFailures:
    async def test_malformed_token_rejected(self, handler, uow):
        with pytest.raises(InvalidVerificationTokenError):
            await handler.handle(
                SignupCommand(
                    verify_token="not-a-uuid", password="password1", device="iPhone"
                )
            )
        assert uow.users.added == []

    async def test_unknown_token_rejected(self, handler, uow):
        with pytest.raises(InvalidVerificationTokenError):
            await handler.handle(
                SignupCommand(
                    verify_token=VerificationToken.generate().value,
                    password="password1",
                    device="iPhone",
                )
            )
        assert uow.users.added == []

    async def test_invalid_password_rejected_before_consuming_token(
        self, handler, uow, token_repo
    ):
        token = await _store_verify_token(token_repo, "user@example.com")

        with pytest.raises(InvalidPasswordError):
            await handler.handle(
                SignupCommand(
                    verify_token=token.value, password="short", device="iPhone"
                )
            )

        assert uow.committed is False
        assert token_repo.deleted == []

    async def test_token_not_consumed_when_commit_fails(
        self, handler, uow, token_repo, monkeypatch
    ):
        token = await _store_verify_token(token_repo, "user@example.com")

        async def _boom():
            raise RuntimeError("commit failed")

        monkeypatch.setattr(uow, "commit", _boom)

        with pytest.raises(RuntimeError):
            await handler.handle(
                SignupCommand(
                    verify_token=token.value, password="password1", device="iPhone"
                )
            )

        assert token_repo.deleted == []

    async def test_no_publisher_still_issues_tokens(
        self, uow, session_repo, encoder, hasher, token_repo
    ):
        handler = SignupHandler(
            uow=uow,
            session_repository=session_repo,
            token_encoder=encoder,
            password_hasher=hasher,
            token_repository=token_repo,
            event_publisher=None,
        )
        token = await _store_verify_token(token_repo, "user@example.com")

        result = await handler.handle(
            SignupCommand(
                verify_token=token.value, password="password1", device="iPhone"
            )
        )
        assert result.access_token
