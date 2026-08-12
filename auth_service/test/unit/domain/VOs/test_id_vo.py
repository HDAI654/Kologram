import pytest
from shared.id_vo import ID
from shared.exceptions import InvalidIDError


class TestID:
    def test_not_str(self):
        with pytest.raises(InvalidIDError):
            ID(123)
            ID(None)
            ID([])

    def test_empty_or_whitespace(self):
        with pytest.raises(InvalidIDError):
            ID("")
            ID(" ")
            ID("    ")

    def test_invalid_uuid_format(self):
        invalid = [
            "not-a-uuid",
            "000-0000-0000-0000-0000",
        ]
        for val in invalid:
            with pytest.raises(InvalidIDError):
                ID(val)

    def test_valid_uuid_v4(self):
        valid = "3bb6a3ca-66dc-440e-8d11-d8cca7ad7792"
        vo = ID(valid)
        assert vo.value == valid

    def test_stripping(self):
        valid = " 3bb6a3ca-66dc-440e-8d11-d8cca7ad7792 "
        vo = ID(valid)
        assert vo.value == valid.strip()

    def test_custom_exception(self):
        class CustomError(Exception):
            pass

        with pytest.raises(CustomError):
            ID("invalid", exc=CustomError)

    def test_generate(self):
        vo = ID.generate()
        # Should be a valid UUID v4 string
        assert isinstance(vo.value, str)
        assert len(vo.value) == 36
        # Optionally check format with uuid.UUID
        import uuid

        uuid_obj = uuid.UUID(vo.value, version=4)
        assert str(uuid_obj) == vo.value
