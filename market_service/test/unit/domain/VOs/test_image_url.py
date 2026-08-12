import pytest

from src.domain.value_objects.image_url import ImageUrl
from src.exceptions import InvalidImageUrlError


def test_https_url() -> None:
    assert ImageUrl("https://cdn.example.com/a.jpg").value.startswith("https://")


def test_relative_url() -> None:
    assert ImageUrl("/media/a.jpg").value == "/media/a.jpg"


def test_invalid_scheme() -> None:
    with pytest.raises(InvalidImageUrlError):
        ImageUrl("ftp://x")
