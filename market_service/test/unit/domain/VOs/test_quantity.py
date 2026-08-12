import pytest

from src.domain.value_objects.quantity import Quantity
from src.exceptions import InvalidQuantityError


def test_quantity_zero_allowed() -> None:
    assert Quantity(0).value == 0


def test_quantity_negative_raises() -> None:
    with pytest.raises(InvalidQuantityError):
        Quantity(-1)


def test_quantity_rejects_bool() -> None:
    with pytest.raises(InvalidQuantityError):
        Quantity(True)  # type: ignore[arg-type]
