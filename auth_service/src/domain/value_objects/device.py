from shared.base_vo import BaseVO
from src.exceptions import InvalidDeviceError


class Device(BaseVO[str]):
    """Opaque device label bound into session tokens."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidDeviceError(
                f"Device must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidDeviceError("Device must be a non-empty string")
        if len(value) > 50:
            raise InvalidDeviceError("Device must be at most 50 characters")
        super().__init__(value)
