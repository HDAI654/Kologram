from __future__ import annotations

import logging

from src.infrastructure.email.console_sender import ConsoleEmailSender


def test_console_sender_logs(caplog) -> None:
    sender = ConsoleEmailSender()
    with caplog.at_level(logging.INFO):
        sender.send(to="a@b.com", subject="Hi", body="Body text")
    assert "a@b.com" in caplog.text
    assert "Hi" in caplog.text
    assert "Body text" in caplog.text
