"""Bcrypt password hasher adapter."""

from __future__ import annotations

import bcrypt

from src.domain.ports.password_hasher import PasswordHasher
from src.domain.value_objects.hashed_password import HashedPassword
from src.domain.value_objects.password import Password


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, password: Password) -> HashedPassword:
        digest = bcrypt.hashpw(
            password.value.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")
        return HashedPassword(digest)

    def verify(self, plain: str, hashed: HashedPassword) -> bool:
        try:
            return bcrypt.checkpw(
                plain.encode("utf-8"),
                hashed.value.encode("utf-8"),
            )
        except Exception:
            return False
