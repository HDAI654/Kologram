import pytest

from src.domain.value_objects.quantity import Quantity
from src.exceptions import InvalidQuantityError


class TestQuantity:
    def test_zero_allowed(self):
        assert Quantity(0).value == 0

    def test_positive(self):
        assert Quantity(5).value == 5

    def test_max_allowed(self):
        assert Quantity(1_000_000).value == 1_000_000

    def test_over_max_rejected(self):
        with pytest.raises(InvalidQuantityError):
            Quantity(1_000_001)

    def test_negative_rejected(self):
        with pytest.raises(InvalidQuantityError):
            Quantity(-1)

    def test_bool_rejected(self):
        with pytest.raises(InvalidQuantityError):
            Quantity(True)
        with pytest.raises(InvalidQuantityError):
            Quantity(False)

    def test_non_int_rejected(self):
        for bad in ("5", 5.0, None):
            with pytest.raises(InvalidQuantityError):
                Quantity(bad)  # type: ignore[arg-type]

    def test_equality_and_hash(self):
        assert Quantity(5) == Quantity(5)
        assert hash(Quantity(5)) == hash(Quantity(5))
