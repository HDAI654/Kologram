import pytest

from src.domain.value_objects.sort_order import SortOrder
from src.exceptions import InvalidSortOrderError


def test_valid() -> None:
    assert SortOrder(0).value == 0
    assert SortOrder(10).value == 10


def test_invalid() -> None:
    with pytest.raises(InvalidSortOrderError):
        SortOrder(-1)
    with pytest.raises(InvalidSortOrderError):
        SortOrder(1001)
    with pytest.raises(InvalidSortOrderError):
        SortOrder(True)  # type: ignore[arg-type]
