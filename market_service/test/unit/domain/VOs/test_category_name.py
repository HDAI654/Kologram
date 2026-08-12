import pytest

from src.domain.value_objects.category_name import CategoryName
from src.exceptions import InvalidCategoryNameError


def test_valid_name() -> None:
    assert CategoryName("Electronics").value == "Electronics"


def test_name_too_short() -> None:
    with pytest.raises(InvalidCategoryNameError):
        CategoryName("A")
