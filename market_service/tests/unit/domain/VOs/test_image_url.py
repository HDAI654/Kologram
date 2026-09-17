import pytest

from src.domain.value_objects.image_url import ImageUrl
from src.exceptions import InvalidImageUrlError

_MAX_LEN = 2048
_PREFIX = "https://example.com/"


class TestImageUrl:
    def test_https_url(self):
        url = "https://example.com/image.jpg"
        assert ImageUrl(url).value == url

    def test_http_url(self):
        url = "http://example.com/image.jpg"
        assert ImageUrl(url).value == url

    def test_relative_url(self):
        assert ImageUrl("/images/cat.png").value == "/images/cat.png"

    def test_strips_whitespace(self):
        assert ImageUrl("  https://x.com/a.png  ").value == "https://x.com/a.png"

    def test_max_length_allowed(self):
        url = _PREFIX + "a" * (_MAX_LEN - len(_PREFIX))
        assert len(url) == _MAX_LEN
        assert ImageUrl(url).value == url

    def test_over_max_length_rejected(self):
        url = _PREFIX + "a" * (_MAX_LEN - len(_PREFIX) + 1)
        with pytest.raises(InvalidImageUrlError):
            ImageUrl(url)

    def test_empty_rejected(self):
        with pytest.raises(InvalidImageUrlError):
            ImageUrl("")

    def test_whitespace_only_rejected(self):
        with pytest.raises(InvalidImageUrlError):
            ImageUrl("   ")

    def test_invalid_scheme_rejected(self):
        with pytest.raises(InvalidImageUrlError):
            ImageUrl("ftp://example.com/a.png")

    def test_missing_scheme_rejected(self):
        with pytest.raises(InvalidImageUrlError):
            ImageUrl("example.com/a.png")

    def test_rejects_non_string(self):
        for bad in (123, None, b"/a"):
            with pytest.raises(InvalidImageUrlError):
                ImageUrl(bad)  # type: ignore[arg-type]

    def test_equality_and_hash(self):
        url = "https://example.com/a.png"
        assert ImageUrl(url) == ImageUrl(url)
        assert hash(ImageUrl(url)) == hash(ImageUrl(url))
