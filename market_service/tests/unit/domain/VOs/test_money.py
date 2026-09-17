from decimal import Decimal

import pytest

from src.domain.value_objects.money import Money
from src.exceptions import InvalidMoneyError


class TestMoneyConstruction:
    def test_valid_decimal(self):
        m = Money(Decimal("10.50"), "USD")
        assert m.amount == Decimal("10.50")
        assert m.currency == "USD"

    def test_valid_str(self):
        assert Money("10.50", "USD").amount == Decimal("10.50")

    def test_valid_int(self):
        assert Money(10, "USD").amount == Decimal("10.00")

    def test_valid_float(self):
        assert Money(10.5, "USD").amount == Decimal("10.50")

    def test_default_currency_is_usd(self):
        assert Money("10.00").currency == "USD"

    @pytest.mark.parametrize("currency", ["USD", "EUR", "GBP", "TRY", "AED"])
    def test_all_allowed_currencies(self, currency):
        assert Money("1.00", currency).currency == currency

    def test_currency_normalized_to_uppercase_and_stripped(self):
        assert Money("1.00", "usd").currency == "USD"
        assert Money("1.00", " eur ").currency == "EUR"

    def test_unsupported_currency_rejected(self):
        with pytest.raises(InvalidMoneyError):
            Money("1.00", "JPY")

    def test_non_string_currency_rejected(self):
        with pytest.raises(InvalidMoneyError):
            Money("1.00", 123)  # type: ignore[arg-type]
        with pytest.raises(InvalidMoneyError):
            Money("1.00", None)  # type: ignore[arg-type]

    def test_empty_currency_rejected(self):
        with pytest.raises(InvalidMoneyError):
            Money("1.00", "")

    def test_zero_allowed(self):
        assert Money("0.00", "USD").amount == Decimal("0.00")

    def test_negative_rejected(self):
        with pytest.raises(InvalidMoneyError):
            Money("-1.00", "USD")

    def test_more_than_two_decimals_rejected(self):
        with pytest.raises(InvalidMoneyError):
            Money("1.234", "USD")

    def test_single_decimal_quantized(self):
        assert Money("1.5", "USD").amount == Decimal("1.50")

    def test_invalid_amount_string_rejected(self):
        with pytest.raises(InvalidMoneyError):
            Money("abc", "USD")

    def test_none_amount_rejected(self):
        with pytest.raises(InvalidMoneyError):
            Money(None, "USD")  # type: ignore[arg-type]

    def test_quantizes_to_two_decimals(self):
        assert Money("10", "USD").amount == Decimal("10.00")
        assert Money("10.5", "USD").amount == Decimal("10.50")


class TestMoneyOperations:
    def test_value_tuple(self):
        assert Money("10.50", "USD").value == (Decimal("10.50"), "USD")

    def test_amount_and_currency_properties(self):
        m = Money("10.50", "EUR")
        assert m.amount == Decimal("10.50")
        assert m.currency == "EUR"

    def test_repr(self):
        assert repr(Money("10.50", "USD")) == "Money(10.50, 'USD')"

    def test_zero_classmethod(self):
        m = Money.zero("EUR")
        assert m.amount == Decimal("0.00")
        assert m.currency == "EUR"

    def test_zero_default_currency(self):
        assert Money.zero().currency == "USD"


class TestMoneyIdentity:
    def test_equality_and_hash(self):
        assert Money("10.00", "USD") == Money("10.00", "USD")
        assert hash(Money("10.00", "USD")) == hash(Money("10.00", "USD"))

    def test_inequality_different_amount(self):
        assert Money("10.00", "USD") != Money("20.00", "USD")

    def test_inequality_different_currency(self):
        assert Money("10.00", "USD") != Money("10.00", "EUR")
