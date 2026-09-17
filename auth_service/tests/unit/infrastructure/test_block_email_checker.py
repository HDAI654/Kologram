import pytest

from src.domain.value_objects.email import Email
from src.infrastructure.cache.config_email_blocklist_checker import (
    ConfigEmailBlocklistChecker,
)
from src.infrastructure.cache.noop_email_blocklist_checker import (
    NoOpEmailBlocklistChecker,
)


@pytest.mark.asyncio
async def test_noop_allows_all() -> None:
    checker = NoOpEmailBlocklistChecker()
    assert await checker.is_blocked(Email("anyone@example.com")) is False


@pytest.mark.asyncio
async def test_config_blocks_address() -> None:
    checker = ConfigEmailBlocklistChecker(
        blocked_emails={"bad@example.com"},
        blocked_domains=set(),
    )
    assert await checker.is_blocked(Email("bad@example.com")) is True
    assert await checker.is_blocked(Email("ok@example.com")) is False


@pytest.mark.asyncio
async def test_config_blocks_domain() -> None:
    checker = ConfigEmailBlocklistChecker(
        blocked_emails=set(),
        blocked_domains={"spam.test"},
    )
    assert await checker.is_blocked(Email("a@spam.test")) is True
    assert await checker.is_blocked(Email("a@good.test")) is False
