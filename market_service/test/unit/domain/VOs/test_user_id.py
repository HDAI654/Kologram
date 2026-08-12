import pytest

from src.domain.value_objects.user_id import UserId
from src.exceptions import InvalidUserIdError


def test_generate_and_parse() -> None:
    uid = UserId.generate()
    assert UserId(uid.value) == uid


def test_invalid() -> None:
    with pytest.raises(InvalidUserIdError):
        UserId("")
    with pytest.raises(InvalidUserIdError):
        UserId("bad")
