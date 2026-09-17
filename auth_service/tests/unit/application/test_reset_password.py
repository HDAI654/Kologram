import pytest

from src.application.reset_password import (
    ResetPasswordCommand,
    ResetPasswordHandler,
)
from src.domain.value_objects.email import Email
from src.domain.value_objects.verification_token import VerificationToken
from src.exceptions import (
    AccountSuspendedError,
    InvalidPasswordError,
    InvalidVerificationTokenError,
    UserNotFoundError,
)


@pytest.fixture
def handler(uow, hasher, token_repo) -> ResetPasswordHandler:
    return ResetPasswordHandler(
        uow=uow,
        password_hasher=hasher,
        token_repository=token_repo,
    )


async def _store_token(token_repo, email: str) -> VerificationToken:
    token = VerificationToken.generate()
    await token_repo.add(
        token=token,
        email=Email(email),
        token_type="forget_pass_verify",
        ttl_seconds=600,
    )
    return token


class TestResetPasswordSuccess:
    async def test_updates_password_and_commits(
        self, handler, uow, token_repo, make_user
    ):
        user = make_user(email="user@example.com")
        await uow.users.add(user)
        token = await _store_token(token_repo, "user@example.com")

        await handler.handle(
            ResetPasswordCommand(verify_token=token.value, new_password="newpass1")
        )

        assert uow.committed is True
        assert len(uow.users.updated) == 1
        user_id, new_hash = uow.users.updated[0]
        assert user_id == user.id
        assert new_hash.value == "hashed::newpass1"

    async def test_consumes_token_after_commit(
        self, handler, uow, token_repo, make_user
    ):
        user = make_user(email="user@example.com")
        await uow.users.add(user)
        token = await _store_token(token_repo, "user@example.com")

        await handler.handle(
            ResetPasswordCommand(verify_token=token.value, new_password="newpass1")
        )

        assert ("forget_pass_verify", token.value) in token_repo.deleted

    async def test_hashes_new_password(
        self, handler, uow, token_repo, hasher, make_user
    ):
        user = make_user(email="user@example.com")
        await uow.users.add(user)
        token = await _store_token(token_repo, "user@example.com")

        await handler.handle(
            ResetPasswordCommand(verify_token=token.value, new_password="newpass1")
        )

        assert hasher.hash_calls == ["newpass1"]


class TestResetPasswordFailures:
    async def test_malformed_token_rejected(self, handler, uow):
        with pytest.raises(InvalidVerificationTokenError):
            await handler.handle(
                ResetPasswordCommand(verify_token="not-a-uuid", new_password="newpass1")
            )
        assert uow.committed is False

    async def test_unknown_token_rejected(self, handler, uow):
        with pytest.raises(InvalidVerificationTokenError):
            await handler.handle(
                ResetPasswordCommand(
                    verify_token=VerificationToken.generate().value,
                    new_password="newpass1",
                )
            )
        assert uow.committed is False

    async def test_invalid_password_rejected_before_lookup(
        self, handler, uow, token_repo, make_user
    ):
        user = make_user(email="user@example.com")
        await uow.users.add(user)
        token = await _store_token(token_repo, "user@example.com")

        with pytest.raises(InvalidPasswordError):
            await handler.handle(
                ResetPasswordCommand(verify_token=token.value, new_password="short")
            )

        assert uow.committed is False
        assert token_repo.deleted == []

    async def test_unknown_user_rolls_back_and_keeps_token(
        self, handler, uow, token_repo
    ):
        token = await _store_token(token_repo, "ghost@example.com")

        with pytest.raises(UserNotFoundError):
            await handler.handle(
                ResetPasswordCommand(verify_token=token.value, new_password="newpass1")
            )

        assert uow.committed is False
        assert uow.rolled_back is True
        assert token_repo.deleted == []
