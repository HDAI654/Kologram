from shared.entity import Entity
from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword
from src.domain.value_objects.user_status import UserStatus
from src.domain.value_objects.user_id import UserId


class User(Entity):
    """Registered account with credentials metadata."""

    def __init__(
        self,
        id: UserId,
        email: Email,
        hashed_password: HashedPassword,
        status: UserStatus | None = None,
    ) -> None:
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.status = status if status is not None else UserStatus.active()
        super().__init__()

    @classmethod
    def create(
        cls,
        email: str,
        hashed_password: str,
        *,
        id: str | None = None,
        status: str | None = None,
    ) -> "User":
        """Factory for a new user."""
        return cls(
            id=UserId(id) if id is not None else UserId.generate(),
            email=Email(email),
            hashed_password=HashedPassword(hashed_password),
            role=UserStatus(status) if status is not None else UserStatus.active(),
        )

    def change_password(self, hashed_password: HashedPassword) -> None:
        """Replace stored password hash."""
        self.hashed_password = hashed_password
