from datetime import date

import pytest

from src.domain.entities.session import Session
from src.domain.value_objects.date import Date
from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.exceptions import (
    InvalidDateError,
    InvalidDeviceError,
    InvalidSessionIdError,
    InvalidUserIdError,
)


@pytest.fixture
def user_id() -> str:
    return UserId.generate().value


class TestSessionCreateDefaults:
    def test_generates_session_id(self, user_id):
        session = Session.create(user_id=user_id)

        assert isinstance(session.id, SessionId)

    def test_binds_user_id(self, user_id):
        session = Session.create(user_id=user_id)

        assert isinstance(session.user_id, UserId)
        assert session.user_id.value == user_id

    def test_device_defaults_to_unknown(self, user_id):
        session = Session.create(user_id=user_id)

        assert isinstance(session.device, Device)
        assert session.device.value == "unknown"

    def test_created_at_defaults_to_today(self, user_id):
        session = Session.create(user_id=user_id)

        assert isinstance(session.created_at, Date)
        assert session.created_at.value == date.today()


class TestSessionCreateExplicitFields:
    def test_explicit_device(self, user_id):
        session = Session.create(user_id=user_id, device="iPhone 15")

        assert session.device.value == "iPhone 15"

    def test_explicit_session_id(self, user_id):
        session_id = SessionId.generate().value
        session = Session.create(user_id=user_id, id=session_id)

        assert session.id.value == session_id

    def test_explicit_created_at_as_iso_string(self, user_id):
        session = Session.create(user_id=user_id, created_at="2024-01-15")

        assert session.created_at.value == date(2024, 1, 15)

    def test_explicit_created_at_as_date_object(self, user_id):
        value = date(2024, 1, 15)
        session = Session.create(user_id=user_id, created_at=value)

        assert session.created_at.value == value

    def test_generated_session_ids_are_unique(self, user_id):
        a = Session.create(user_id=user_id)
        b = Session.create(user_id=user_id)

        assert a.id != b.id


class TestSessionCreateRejections:
    def test_invalid_user_id(self):
        with pytest.raises(InvalidUserIdError):
            Session.create(user_id="not-a-uuid")

    def test_invalid_device(self, user_id):
        with pytest.raises(InvalidDeviceError):
            Session.create(user_id=user_id, device="")

    def test_invalid_session_id(self, user_id):
        with pytest.raises(InvalidSessionIdError):
            Session.create(user_id=user_id, id="not-a-uuid")

    def test_invalid_created_at_string(self, user_id):
        with pytest.raises(InvalidDateError):
            Session.create(user_id=user_id, created_at="not-a-date")


class TestSessionConstructor:
    def test_direct_construction(self):
        session = Session(
            id=SessionId.generate(),
            user_id=UserId.generate(),
            device=Device("iPhone"),
            created_at=Date(date(2024, 1, 15)),
        )

        assert session.device.value == "iPhone"
        assert session.created_at.value == date(2024, 1, 15)


class TestSessionIdentity:
    def test_equal_when_all_attributes_match(self, user_id):
        session_id = SessionId.generate().value
        a = Session.create(user_id=user_id, id=session_id)
        b = Session.create(user_id=user_id, id=session_id)

        assert a == b

    def test_not_equal_when_device_differs(self, user_id):
        session_id = SessionId.generate().value
        a = Session.create(user_id=user_id, id=session_id, device="iPhone")
        b = Session.create(user_id=user_id, id=session_id, device="Pixel")

        assert a != b
