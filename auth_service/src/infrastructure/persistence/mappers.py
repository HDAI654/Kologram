from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword
from src.domain.value_objects.role import Role
from src.domain.value_objects.user_id import UserId
from src.infrastructure.persistence.models.user import UserModel


def model_to_user(model: UserModel) -> User:
    return User(
        id=UserId(model.id),
        email=Email(model.email),
        hashed_password=HashedPassword(model.hashed_password),
        role=Role(model.role),
    )


def user_to_model(user: User) -> UserModel:
    return UserModel(
        id=user.id.value,
        email=user.email.value,
        hashed_password=user.hashed_password.value,
        role=user.role.value,
    )
