from datetime import date
from shared.base_vo import BaseVO
from src.exceptions import InvalidDateError


class Date(BaseVO[date]):
    """ISO calendar date for session metadata."""

    def __init__(self, value: str | date) -> None:
        if isinstance(value, date) and not isinstance(value, type):
            parsed = value
        elif isinstance(value, str):
            try:
                parsed = date.fromisoformat(value.strip())
            except Exception as exc:
                raise InvalidDateError("Date got invalid value") from exc
        else:
            raise InvalidDateError(
                f"Date must be string or datetime.date, got {type(value).__name__}"
            )
        super().__init__(parsed)
