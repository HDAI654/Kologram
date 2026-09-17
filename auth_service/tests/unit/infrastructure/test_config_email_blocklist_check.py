import pytest
from src.domain.value_objects.email import Email
from src.infrastructure.cache.config_email_blocklist_checker import (
    ConfigEmailBlocklistChecker,
)


class TestConfigEmailBlocklistChecker:
    async def test_blocks_exact_email(self):
        checker = ConfigEmailBlocklistChecker(
            blocked_emails={"spam@example.com"}, blocked_domains=set()
        )
        assert await checker.is_blocked(Email("spam@example.com")) is True

    async def test_does_not_block_unknown_email(self):
        checker = ConfigEmailBlocklistChecker(
            blocked_emails={"spam@example.com"}, blocked_domains=set()
        )
        assert await checker.is_blocked(Email("user@example.com")) is False

    async def test_blocks_entire_domain(self):
        checker = ConfigEmailBlocklistChecker(
            blocked_emails=set(), blocked_domains={"blocked.test"}
        )
        assert await checker.is_blocked(Email("anyone@blocked.test")) is True

    async def test_domain_match_is_case_insensitive(self):
        checker = ConfigEmailBlocklistChecker(
            blocked_emails=set(), blocked_domains={"blocked.test"}
        )
        assert await checker.is_blocked(Email("user@Blocked.Test")) is True

    async def test_unrelated_domain_not_blocked(self):
        checker = ConfigEmailBlocklistChecker(
            blocked_emails=set(), blocked_domains={"blocked.test"}
        )
        assert await checker.is_blocked(Email("user@example.com")) is False

    async def test_email_lookup_is_case_insensitive(self):
        checker = ConfigEmailBlocklistChecker(
            blocked_emails={"Spam@Example.com".lower()}, blocked_domains=set()
        )
        assert await checker.is_blocked(Email("SPAM@example.com")) is True

    async def test_no_emails_returns_false(self):
        checker = ConfigEmailBlocklistChecker(
            blocked_emails=set(), blocked_domains=set()
        )
        assert await checker.is_blocked(Email("user@example.com")) is False
