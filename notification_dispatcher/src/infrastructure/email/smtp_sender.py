"""SMTP plain-text email sender."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from src.domain.ports.email_sender import EmailSender
from src.exceptions import EmailSendError

logger = logging.getLogger(__name__)


class SmtpEmailSender(EmailSender):
    def __init__(
        self,
        *,
        host: str,
        port: int,
        user: str,
        password: str,
        from_addr: str,
        use_tls: bool = True,
        use_ssl: bool = False,
    ) -> None:
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._from = from_addr
        self._use_tls = use_tls
        self._use_ssl = use_ssl

    def send(self, *, to: str, subject: str, body: str) -> None:
        msg = EmailMessage()
        msg["From"] = self._from
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        try:
            if self._use_ssl:
                with smtplib.SMTP_SSL(self._host, self._port, timeout=30) as smtp:
                    if self._user:
                        smtp.login(self._user, self._password)
                    smtp.send_message(msg)
            else:
                with smtplib.SMTP(self._host, self._port, timeout=30) as smtp:
                    smtp.ehlo()
                    if self._use_tls:
                        smtp.starttls()
                        smtp.ehlo()
                    if self._user:
                        smtp.login(self._user, self._password)
                    smtp.send_message(msg)
        except Exception as exc:
            logger.warning("smtp send failed to=%s error=%s", to, exc)
            raise EmailSendError(str(exc)) from exc
