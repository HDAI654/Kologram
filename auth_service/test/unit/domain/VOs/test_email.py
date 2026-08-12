import pytest
from src.domain.value_objects.email import Email
from src.exceptions import InvalidEmailError


class TestEmail:
    def test_not_str_email(self):
        with pytest.raises(InvalidEmailError):
            Email(123)
            Email(None)
            Email([])

    def test_empty_str_email(self):
        with pytest.raises(InvalidEmailError):
            Email("")
            Email(" ")
            Email("    ")

    def test_invalid_format(self):
        invalid_emails = [
            "plainaddress",
            "@missingusername.com",
            "username@.com",
            "username@domain",
            "username@domain.",
            "user name@domain.com",
        ]
        for email in invalid_emails:
            with pytest.raises(InvalidEmailError):
                Email(email)

    def test_too_long_email(self):
        local = "a" * 200
        domain = "b" * 50
        long_email = f"{local}@{domain}.com"
        # total length > 254
        with pytest.raises(InvalidEmailError):
            Email(long_email)

    def test_valid_email_normalization(self):
        email_str = "  Test@Example.COM  "
        vo = Email(email_str)
        assert vo.value == "test@example.com"

    def test_valid_email(self):
        vo = Email("user@domain.com")
        assert vo.value == "user@domain.com"
