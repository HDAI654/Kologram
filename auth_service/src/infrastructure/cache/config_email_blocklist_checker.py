from src.conf import Config
from src.domain.ports.email_blocklist_checker import EmailBlocklistChecker
from src.domain.value_objects.email import Email


class ConfigEmailBlocklistChecker(EmailBlocklistChecker):
    """Blocks addresses listed in BLOCKED_EMAILS or matching BLOCKED_EMAIL_DOMAINS."""

    def __init__(
        self,
        blocked_emails: set[str] | None = None,
        blocked_domains: set[str] | None = None,
    ) -> None:
        self._emails = (
            blocked_emails if blocked_emails is not None else set(Config.BLOCKED_EMAILS)
        )
        self._domains = (
            blocked_domains
            if blocked_domains is not None
            else set(Config.BLOCKED_EMAIL_DOMAINS)
        )

    async def is_blocked(self, email: Email) -> bool:
        value = email.value.lower()
        if value in self._emails:
            return True
        domain = value.rsplit("@", 1)[-1]
        return domain in self._domains
