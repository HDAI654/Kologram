import pytest
from src.domain.value_objects.device import Device
from src.exceptions import InvalidDeviceError


class TestDevice:
    def test_not_str_device(self):
        with pytest.raises(InvalidDeviceError):
            Device(25)
            Device(None)

    def test_empty_str_device(self):
        with pytest.raises(InvalidDeviceError):
            Device("")
            Device(" ")
            Device("    ")

    def test_device_strip(self):
        str_device = "        device  "
        device = Device(str_device)
        assert device.value == str_device.strip()

    def test_long_device(self):
        with pytest.raises(InvalidDeviceError):
            Device("A" * 51)
