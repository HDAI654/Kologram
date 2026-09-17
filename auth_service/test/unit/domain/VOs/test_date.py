from datetime import date, datetime, timezone
import pytest
from src.domain.value_objects.date import Date
from src.exceptions import InvalidDateError


class TestDateConstruction:
    def test_from_iso_string(self):
        assert Date("2024-01-15").value == date(2024, 1, 15)

    def test_from_date_object(self):
        value = date(2024, 1, 15)
        assert Date(value).value == value

    def test_strips_whitespace_before_parsing(self):
        assert Date("  2024-01-15  ").value == date(2024, 1, 15)

    def test_accepts_boundary_leap_day(self):
        assert Date("2024-02-29").value == date(2024, 2, 29)


class TestDateRejections:
    @pytest.mark.parametrize(
        "value",
        ["", "   ", "not-a-date", "2024/01/15", "2024-13-01", "2024-02-30"],
    )
    def test_invalid_string_raises(self, value):
        with pytest.raises(InvalidDateError):
            Date(value)

    @pytest.mark.parametrize("value", [123, None, [], {}, 1.5])
    def test_non_string_non_date_raises(self, value):
        with pytest.raises(InvalidDateError):
            Date(value)  # type: ignore[arg-type]

    def test_invalid_string_preserves_cause(self):
        with pytest.raises(InvalidDateError) as exc_info:
            Date("not-a-date")
        assert exc_info.value.__cause__ is not None


class TestDateIdentity:
    def test_equality_and_hash(self):
        assert Date("2024-01-15") == Date("2024-01-15")
        assert hash(Date("2024-01-15")) == hash(Date("2024-01-15"))

    def test_inequality(self):
        assert Date("2024-01-15") != Date("2024-01-16")


class TestDateKnownEdgeCase:
    def test_datetime_bypasses_parsing_and_is_stored_as_is(self):
        moment = datetime(2024, 1, 15, 12, 30, tzinfo=timezone.utc)

        vo = Date(moment)

        assert vo.value is moment
