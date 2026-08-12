import pytest
from datetime import date
from src.domain.entities.session import Session
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.domain.value_objects.device import Device
from src.domain.value_objects.date import Date
from src.exceptions import InvalidUserIdError, InvalidDeviceError, InvalidDateError


class TestSession:
    def test_init_valid(self):
        session_id = SessionId("3bb6a3ca-66dc-440e-8d11-d8cca7ad7792")
        user_id = UserId("3bb6a3ca-66dc-440e-8d11-d8cca7ad7793")
        device = Device("iPhone 12")
        created_at = Date("2026-08-12")
        session = Session(session_id, user_id, device, created_at)
        assert session.id == session_id
        assert session.user_id == user_id
        assert session.device == device
        assert session.created_at == created_at

    def test_create_defaults(self):
        user_id_str = "3bb6a3ca-66dc-440e-8d11-d8cca7ad7794"
        session = Session.create(user_id=user_id_str)
        assert isinstance(session.id, SessionId)
        assert session.user_id.value == user_id_str
        assert session.device.value == "unknown"
        assert session.created_at.value == date.today()

    def test_create_with_custom_values(self):
        user_id_str = "3bb6a3ca-66dc-440e-8d11-d8cca7ad7795"
        id_str = "3bb6a3ca-66dc-440e-8d11-d8cca7ad7796"
        device_str = "Chrome on Windows"
        created_at_str = "2025-01-01"
        session = Session.create(
            user_id=user_id_str,
            device=device_str,
            id=id_str,
            created_at=created_at_str,
        )
        assert session.id.value == id_str
        assert session.user_id.value == user_id_str
        assert session.device.value == device_str
        assert session.created_at.value == date(2025, 1, 1)

    def test_create_invalid_user_id(self):
        with pytest.raises(InvalidUserIdError):
            Session.create(user_id="not-a-uuid")

    def test_create_invalid_device(self):
        with pytest.raises(InvalidDeviceError):
            Session.create(user_id="3bb6a3ca-66dc-440e-8d11-d8cca7ad7797", device="")

    def test_create_invalid_created_at(self):
        with pytest.raises(InvalidDateError):
            Session.create(
                user_id="3bb6a3ca-66dc-440e-8d11-d8cca7ad7798",
                created_at="invalid-date",
            )

    def test_create_created_at_date_object(self):
        dt = date(2024, 12, 31)
        session = Session.create(
            user_id="3bb6a3ca-66dc-440e-8d11-d8cca7ad7799",
            created_at=dt,
        )
        assert session.created_at.value == dt
