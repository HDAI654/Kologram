from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.exceptions import EmailSendError
from src.infrastructure.email.smtp_sender import SmtpEmailSender


def test_smtp_send_success() -> None:
    sender = SmtpEmailSender(
        host="localhost",
        port=587,
        user="u",
        password="p",
        from_addr="from@x.com",
        use_tls=True,
        use_ssl=False,
    )
    mock_smtp = MagicMock()
    mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
    mock_smtp.__exit__ = MagicMock(return_value=False)
    with patch("src.infrastructure.email.smtp_sender.smtplib.SMTP", return_value=mock_smtp):
        sender.send(to="a@b.com", subject="S", body="B")
    mock_smtp.send_message.assert_called_once()


def test_smtp_send_failure_raises() -> None:
    sender = SmtpEmailSender(
        host="localhost",
        port=587,
        user="",
        password="",
        from_addr="from@x.com",
        use_tls=False,
        use_ssl=False,
    )
    mock_smtp = MagicMock()
    mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
    mock_smtp.__exit__ = MagicMock(return_value=False)
    mock_smtp.send_message.side_effect = OSError("down")
    with patch("src.infrastructure.email.smtp_sender.smtplib.SMTP", return_value=mock_smtp):
        with pytest.raises(EmailSendError):
            sender.send(to="a@b.com", subject="S", body="B")
