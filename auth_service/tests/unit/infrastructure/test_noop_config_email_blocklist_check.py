from src.domain.value_objects.email import Email
from src.infrastructure.cache.noop_email_blocklist_checker import (
    NoOpEmailBlocklistChecker,
)


class TestNoOpEmailBlocklistChecker:
    async def test_never_blocks(self):
        checker = NoOpEmailBlocklistChecker()
        assert await checker.is_blocked(Email("user@example.com")) is False

    async def test_never_blocks_arbitrary_domain(self):
        checker = NoOpEmailBlocklistChecker()
        assert await checker.is_blocked(Email("spam@bad.test")) is False
