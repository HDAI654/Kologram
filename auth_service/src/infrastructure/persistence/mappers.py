from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword
from src.domain.value_objects.user_status import UserStatus
from src.domain.value_objects.user_id import UserId
from src.infrastructure.persistence.models.user import UserModel


def model_to_user(model: UserModel) -> User:
    return User(
        id=UserId(model.id),
        email=Email(model.email),
        hashed_password=HashedPassword(model.hashed_password),
        status=UserStatus(model.status),
    )


def user_to_model(user: User) -> UserModel:
    return UserModel(
        id=user.id.value,
        email=user.email.value,
        hashed_password=user.hashed_password.value,
        status=user.status.value,
    )
