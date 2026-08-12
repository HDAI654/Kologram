from abc import ABC, abstractmethod
from src.domain.value_objects.hashed_password import HashedPassword
from src.domain.value_objects.password import Password


class PasswordHasher(ABC):
    """Hashes plain passwords and verifies against stored hashes."""

    @abstractmethod
    def hash(self, password: Password) -> HashedPassword:
        raise NotImplementedError

    @abstractmethod
    def verify(self, plain: str, hashed: HashedPassword) -> bool:
        """Verify plain input against stored hash without strength rules."""
        raise NotImplementedError
