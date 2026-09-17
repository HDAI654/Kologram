"""Unit tests for RedisVerificationTokenRepository (mocked client)."""

from unittest.mock import AsyncMock

import pytest

from src.domain.value_objects.email import Email
from src.domain.value_objects.verification_token import VerificationToken
from src.infrastructure.cache.redis_verification_token_repository import (
    RedisVerificationTokenRepository,
)


@pytest.mark.asyncio
async def test_add_get_delete() -> None:
    client = AsyncMock()
    client.setex = AsyncMock()
    client.get = AsyncMock(return_value=b"a@b.com")
    client.delete = AsyncMock(return_value=1)
    repo = RedisVerificationTokenRepository(client)
    token = VerificationToken.generate()

    await repo.add(token, Email("a@b.com"), "verifyemail", 60)
    client.setex.assert_awaited_once()

    email = await repo.get(token, "verifyemail")
    assert email is not None
    assert email.value == "a@b.com"

    await repo.delete(token, "verifyemail")
    client.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_miss() -> None:
    client = AsyncMock()
    client.get = AsyncMock(return_value=None)
    repo = RedisVerificationTokenRepository(client)
    assert await repo.get(VerificationToken.generate(), "verifyemail") is None
