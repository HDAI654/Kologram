import pytest
from datetime import date
from src.domain.value_objects.date import Date
from src.exceptions import InvalidDateError


class TestDate:
    def test_invalid_types(self):
        with pytest.raises(InvalidDateError):
            Date(123)
            Date(None)
            Date([])

    def test_invalid_string_format(self):
        with pytest.raises(InvalidDateError):
            Date("2025-13-01")   # invalid month
            Date("2025-01-32")   # invalid day
            Date("not-a-date")

    def test_valid_date_object(self):
        d = date(2026, 8, 12)
        vo = Date(d)
        assert vo.value == d

    def test_valid_string(self):
        vo = Date("2026-08-12")
        assert vo.value == date(2026, 8, 12)

    def test_string_stripping(self):
        vo = Date("  2026-08-12  ")
        assert vo.value == date(2026, 8, 12)

    def test_empty_string(self):
        with pytest.raises(InvalidDateError):
            Date("")
            Date(" ")
            Date("    ")