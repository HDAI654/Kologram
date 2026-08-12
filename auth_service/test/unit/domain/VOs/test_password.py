import pytest
from src.domain.value_objects.password import Password
from src.exceptions import InvalidPasswordError


class TestPassword:
    def test_not_str(self):
        with pytest.raises(InvalidPasswordError):
            Password(123)
            Password(None)

    def test_too_short(self):
        with pytest.raises(InvalidPasswordError):
            Password("Ab1")   # length 3

    def test_too_long(self):
        with pytest.raises(InvalidPasswordError):
            Password("A" * 129 + "1")  # length 130

    def test_no_letter(self):
        with pytest.raises(InvalidPasswordError):
            Password("12345678")  # no letter

    def test_no_digit(self):
        with pytest.raises(InvalidPasswordError):
            Password("abcdefgh")  # no digit

    def test_valid_password(self):
        pw = "ValidPass123"
        vo = Password(pw)
        assert vo.value == pw

    def test_whitespace_not_stripped(self):
        # Stripping is not done, so spaces are allowed but count as characters
        vo = Password(" Valid1 ")
        assert vo.value == " Valid1 "  # exact as given (includes spaces)