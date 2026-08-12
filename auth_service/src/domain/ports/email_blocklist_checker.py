from abc import ABC, abstractmethod
from src.domain.value_objects.email import Email


class EmailBlocklistChecker(ABC):
    """Returns whether an email address is blocked from signup."""

    @abstractmethod
    async def is_blocked(self, email: Email) -> bool:
        raise NotImplementedError
