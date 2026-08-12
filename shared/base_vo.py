from typing import Generic, TypeVar

T = TypeVar("T")


class BaseVO(Generic[T]):
    def __init__(self, value: T):
        self._value = value

    @property
    def value(self) -> T:
        return self._value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    def __eq__(self, other) -> bool:
        return self.__class__ is other.__class__ and self.value == other.value

    def __hash__(self) -> int:
        return hash((self.__class__, self.value))
