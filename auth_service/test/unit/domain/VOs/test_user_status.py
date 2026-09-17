import pytest

from src.domain.value_objects.user_status import UserStatus
from src.exceptions import InvalidUserStatusError


class TestUserStatusValues:
    def test_active(self):
        assert UserStatus("ACTIVE").value == "ACTIVE"

    def test_suspended(self):
        assert UserStatus("SUSPENDED").value == "SUSPENDED"

    def test_lowercase_normalized(self):
        assert UserStatus("active").value == "ACTIVE"

    def test_mixed_case_normalized(self):
        assert UserStatus("Suspended").value == "SUSPENDED"

    def test_whitespace_stripped(self):
        assert UserStatus("  active  ").value == "ACTIVE"

    def test_classmethod_active(self):
        assert UserStatus.active().value == "ACTIVE"

    def test_classmethod_suspended(self):
        assert UserStatus.suspended().value == "SUSPENDED"


class TestUserStatusPredicate:
    def test_is_active_true_for_active(self):
        assert UserStatus("ACTIVE").is_active is True

    def test_is_active_false_for_suspended(self):
        assert UserStatus("SUSPENDED").is_active is False


class TestUserStatusRejections:
    @pytest.mark.parametrize("value", ["PENDING", "DELETED", "", "   ", "active-ish"])
    def test_invalid_value_rejected(self, value):
        with pytest.raises(InvalidUserStatusError):
            UserStatus(value)

    @pytest.mark.parametrize("value", [123, None, b"ACTIVE", 1.5])
    def test_non_string_rejected(self, value):
        with pytest.raises(InvalidUserStatusError):
            UserStatus(value)  # type: ignore[arg-type]


class TestUserStatusIdentity:
    def test_equality_and_hash_are_case_insensitive(self):
        assert UserStatus("active") == UserStatus("ACTIVE")
        assert hash(UserStatus("active")) == hash(UserStatus("ACTIVE"))

    def test_inequality(self):
        assert UserStatus("ACTIVE") != UserStatus("SUSPENDED")
