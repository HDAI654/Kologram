import pytest

from src.domain.value_objects.sort_order import SortOrder
from src.exceptions import InvalidSortOrderError


class TestSortOrder:
    def test_zero_allowed(self):
        assert SortOrder(0).value == 0

    def test_positive(self):
        assert SortOrder(100).value == 100

    def test_max_allowed(self):
        assert SortOrder(1000).value == 1000

    def test_over_max_rejected(self):
        with pytest.raises(InvalidSortOrderError):
            SortOrder(1001)

    def test_negative_rejected(self):
        with pytest.raises(InvalidSortOrderError):
            SortOrder(-1)

    def test_bool_rejected(self):
        with pytest.raises(InvalidSortOrderError):
            SortOrder(True)
        with pytest.raises(InvalidSortOrderError):
            SortOrder(False)

    def test_non_int_rejected(self):
        for bad in ("1", 1.0, None):
            with pytest.raises(InvalidSortOrderError):
                SortOrder(bad)  # type: ignore[arg-type]

    def test_equality_and_hash(self):
        assert SortOrder(1) == SortOrder(1)
        assert hash(SortOrder(1)) == hash(SortOrder(1))