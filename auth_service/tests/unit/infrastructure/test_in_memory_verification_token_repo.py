import pytest

from src.domain.value_objects.email import Email
from src.domain.value_objects.verification_token import VerificationToken
from src.infrastructure.cache.in_memory_verification_token_repository import (
    InMemoryVerificationTokenRepository,
)


@pytest.fixture
def repo() -> InMemoryVerificationTokenRepository:
    return InMemoryVerificationTokenRepository()


class TestAddAndGet:
    async def test_roundtrip(self, repo):
        token = VerificationToken.generate()
        await repo.add(
            token=token,
            email=Email("user@example.com"),
            token_type="verifyemail",
            ttl_seconds=600,
        )
        result = await repo.get(token, "verifyemail")
        assert result is not None
        assert result.value == "user@example.com"

    async def test_returns_none_when_missing(self, repo):
        assert await repo.get(VerificationToken.generate(), "verifyemail") is None

    async def test_same_value_under_different_type_is_isolated(self, repo):
        token = VerificationToken.generate()
        await repo.add(
            token=token,
            email=Email("a@example.com"),
            token_type="verifyemail",
            ttl_seconds=600,
        )
        assert await repo.get(token, "forget_pass_verify") is None


class TestDelete:
    async def test_delete_removes_token(self, repo):
        token = VerificationToken.generate()
        await repo.add(
            token=token,
            email=Email("user@example.com"),
            token_type="verifyemail",
            ttl_seconds=600,
        )

        await repo.delete(token, "verifyemail")

        assert await repo.get(token, "verifyemail") is None

    async def test_delete_missing_is_idempotent(self, repo):
        await repo.delete(VerificationToken.generate(), "verifyemail")
