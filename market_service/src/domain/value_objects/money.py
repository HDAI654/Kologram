from decimal import Decimal, InvalidOperation
from typing import Self

from shared.base_vo import BaseVO
from src.exceptions import InvalidMoneyError

_ALLOWED_CURRENCIES = frozenset({"USD", "EUR", "GBP", "TRY", "AED"})


class Money(BaseVO[tuple[Decimal, str]]):
    """Immutable monetary amount with ISO currency code."""

    def __init__(
        self, amount: Decimal | str | int | float, currency: str = "USD"
    ) -> None:
        if not isinstance(currency, str):
            raise InvalidMoneyError(
                f"Currency must be string, got {type(currency).__name__}"
            )
        currency = currency.strip().upper()
        if currency not in _ALLOWED_CURRENCIES:
            raise InvalidMoneyError(f"Unsupported currency: {currency}")

        try:
            decimal_amount = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise InvalidMoneyError(f"Invalid amount: {amount}") from exc

        if decimal_amount < 0:
            raise InvalidMoneyError("Amount must be non-negative")
        quantized = decimal_amount.quantize(Decimal("0.01"))
        if decimal_amount != quantized:
            raise InvalidMoneyError("Amount must have at most 2 decimal places")

        super().__init__((quantized, currency))

    @property
    def amount(self) -> Decimal:
        return self.value[0]

    @property
    def currency(self) -> str:
        return self.value[1]

    @classmethod
    def zero(cls, currency: str = "USD") -> Self:
        """Zero money in the given currency."""
        return cls(Decimal("0.00"), currency)

    def __repr__(self) -> str:
        return f"Money({self.amount}, {self.currency!r})"
