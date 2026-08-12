import pytest
from src.domain.value_objects.user_status import UserStatus
from src.exceptions import InvalidUserStatusError


class TestUserStatus:
    def test_not_str(self):
        with pytest.raises(InvalidUserStatusError):
            UserStatus(123)
            UserStatus(None)
            UserStatus([])

    def test_invalid_values(self):
        invalid = ["", " ", "activeee", "INACTIVE", "PENDING"]
        for val in invalid:
            with pytest.raises(InvalidUserStatusError):
                UserStatus(val)

    def test_valid_values(self):
        for status in ("ACTIVE", "SUSPENDED"):
            vo = UserStatus(status)
            assert vo.value == status

    def test_normalization_strip_upper(self):
        vo = UserStatus("  active  ")
        assert vo.value == "ACTIVE"

    def test_factory_active(self):
        vo = UserStatus.active()
        assert vo.value == "ACTIVE"
        assert vo.is_active is True

    def test_factory_suspended(self):
        vo = UserStatus.suspended()
        assert vo.value == "SUSPENDED"
        assert vo.is_active is False

    def test_is_active_property(self):
        assert UserStatus("ACTIVE").is_active is True
        assert UserStatus("SUSPENDED").is_active is False
