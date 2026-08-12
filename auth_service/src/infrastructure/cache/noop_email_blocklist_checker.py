from src.domain.ports.email_blocklist_checker import EmailBlocklistChecker
from src.domain.value_objects.email import Email


class NoOpEmailBlocklistChecker(EmailBlocklistChecker):
    async def is_blocked(self, email: Email) -> bool:
        return False
