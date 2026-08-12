from decimal import Decimal

import pytest

from src.domain.value_objects.money import Money
from src.exceptions import InvalidMoneyError


def test_money_valid() -> None:
    m = Money("19.99", "USD")
    assert m.amount == Decimal("19.99")
    assert m.currency == "USD"


def test_money_rejects_negative() -> None:
    with pytest.raises(InvalidMoneyError):
        Money("-1", "USD")


def test_money_rejects_unknown_currency() -> None:
    with pytest.raises(InvalidMoneyError):
        Money("10", "XYZ")


def test_money_rejects_excess_precision() -> None:
    with pytest.raises(InvalidMoneyError):
        Money("1.999", "USD")


def test_money_equality() -> None:
    assert Money("10.00", "USD") == Money(10, "USD")


def test_money_zero() -> None:
    assert Money.zero("EUR").amount == Decimal("0.00")
