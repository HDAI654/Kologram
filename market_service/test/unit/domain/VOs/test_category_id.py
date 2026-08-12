import pytest

from src.domain.value_objects.category_id import CategoryId
from src.exceptions import InvalidCategoryIdError


def test_generate_and_parse() -> None:
    cid = CategoryId.generate()
    assert CategoryId(cid.value) == cid


def test_invalid() -> None:
    with pytest.raises(InvalidCategoryIdError):
        CategoryId("")
    with pytest.raises(InvalidCategoryIdError):
        CategoryId("not-uuid")
    with pytest.raises(InvalidCategoryIdError):
        CategoryId(123)  # type: ignore[arg-type]
