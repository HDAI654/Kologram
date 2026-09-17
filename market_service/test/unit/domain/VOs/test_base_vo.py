from src.domain.value_objects.base_vo import BaseVO


class _StringVO(BaseVO[str]):
    pass


class _IntVO(BaseVO[int]):
    pass


class TestBaseVO:
    def test_value_property(self):
        assert _StringVO("hello").value == "hello"
        assert _IntVO(42).value == 42

    def test_str(self):
        assert str(_StringVO("hello")) == "hello"
        assert str(_IntVO(42)) == "42"

    def test_repr(self):
        assert repr(_StringVO("hello")) == "_StringVO('hello')"
        assert repr(_IntVO(42)) == "_IntVO(42)"

    def test_eq_same_class_same_value(self):
        assert _StringVO("a") == _StringVO("a")

    def test_eq_same_class_different_value(self):
        assert _StringVO("a") != _StringVO("b")

    def test_eq_different_class_same_value(self):
        assert _StringVO("1") != _IntVO(1)

    def test_eq_with_non_vo(self):
        assert _StringVO("a") != "a"
        assert _StringVO("a") != None  # noqa: E711

    def test_hash_same_class_same_value(self):
        assert hash(_StringVO("a")) == hash(_StringVO("a"))

    def test_hash_usable_in_set_and_dict(self):
        assert len({_StringVO("a"), _StringVO("a"), _StringVO("b")}) == 2
        assert {_StringVO("a"): 1}[_StringVO("a")] == 1

    def test_hash_differs_by_class(self):
        assert hash(_StringVO("1")) != hash(_IntVO(1))