import pytest

from src.domain.value_objects.device import Device
from src.exceptions import InvalidDeviceError


class TestDevice:
    def test_valid_label(self):
        assert Device("iPhone 15").value == "iPhone 15"

    def test_strips_whitespace(self):
        assert Device("  iPhone 15  ").value == "iPhone 15"

    def test_max_length_boundary(self):
        value = "x" * 50
        assert Device(value).value == value

    def test_over_max_length_rejected(self):
        with pytest.raises(InvalidDeviceError):
            Device("x" * 51)

    def test_empty_string_rejected(self):
        with pytest.raises(InvalidDeviceError):
            Device("")

    def test_whitespace_only_rejected(self):
        with pytest.raises(InvalidDeviceError):
            Device("    ")

    @pytest.mark.parametrize("value", [123, None, b"x", 1.5])
    def test_non_string_rejected(self, value):
        with pytest.raises(InvalidDeviceError):
            Device(value)  # type: ignore[arg-type]

    def test_equality_and_hash(self):
        assert Device("iPhone") == Device("iPhone")
        assert hash(Device("iPhone")) == hash(Device("iPhone"))
