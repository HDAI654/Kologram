import pytest

from src.domain.value_objects.category_name import CategoryName
from src.exceptions import InvalidCategoryNameError


class TestCategoryName:
    def test_min_length_allowed(self):
        assert CategoryName("ab").value == "ab"

    def test_max_length_allowed(self):
        text = "a" * 80
        assert CategoryName(text).value == text

    def test_below_min_rejected(self):
        with pytest.raises(InvalidCategoryNameError):
            CategoryName("a")

    def test_empty_rejected(self):
        with pytest.raises(InvalidCategoryNameError):
            CategoryName("")

    def test_whitespace_only_rejected(self):
        with pytest.raises(InvalidCategoryNameError):
            CategoryName("   ")

    def test_above_max_rejected(self):
        with pytest.raises(InvalidCategoryNameError):
            CategoryName("a" * 81)

    def test_normalizes_whitespace(self):
        assert CategoryName("  Hello   World  ").value == "Hello World"

    def test_length_checked_after_normalization(self):
        with pytest.raises(InvalidCategoryNameError):
            CategoryName(" a ")

    def test_rejects_non_string(self):
        for bad in (123, None, b"ab"):
            with pytest.raises(InvalidCategoryNameError):
                CategoryName(bad)  # type: ignore[arg-type]

    def test_equality_and_hash(self):
        assert CategoryName("Home") == CategoryName("Home")
        assert hash(CategoryName("Home")) == hash(CategoryName("Home"))

    def test_str_and_repr(self):
        vo = CategoryName("Home")
        assert str(vo) == "Home"
        assert repr(vo) == "CategoryName('Home')"