"""SMTP email adapter (optional production path)."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage as StdEmailMessage

from src.conf import Config
from src.domain.notifications.email_message import EmailMessage
from src.domain.ports.email_sender import EmailSender
from src.exceptions import EmailDeliveryError

logger = logging.getLogger(__name__)


class SMTPEmailSender(EmailSender):
    """Minimal SMTP sender. Rendering is deferred: body is structured context JSON."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        use_tls: bool | None = None,
        from_address: str | None = None,
    ) -> None:
        self._host = host or Config.SMTP_HOST
        self._port = port if port is not None else Config.SMTP_PORT
        self._user = user if user is not None else Config.SMTP_USER
        self._password = password if password is not None else Config.SMTP_PASSWORD
        self._use_tls = use_tls if use_tls is not None else Config.SMTP_USE_TLS
        self._from = from_address or Config.EMAIL_FROM

    async def send(self, message: EmailMessage) -> None:
        # Template rendering is out of scope; send structured placeholder body.
        # Next engineer replaces body with real templates using message.context.
        safe_context = {
            k: ("***" if k == "token" else v) for k, v in message.context.items()
        }
        body_lines = [
            f"[template:{message.template_key}]",
            f"[subject_key:{message.subject_key}]",
            *(f"{k}={v}" for k, v in sorted(safe_context.items())),
        ]
        if "token" in message.context:
            # Required by VerificationTokenCreated: include real token only in body.
            body_lines.append(f"your verification token is {message.context['token']}")

        msg = StdEmailMessage()
        msg["From"] = message.from_address or self._from
        msg["To"] = message.to
        msg["Subject"] = f"[{message.subject_key}] notification"
        msg.set_content("\n".join(body_lines))

        try:
            with smtplib.SMTP(self._host, self._port, timeout=15) as smtp:
                if self._use_tls:
                    smtp.starttls()
                if self._user:
                    smtp.login(self._user, self._password)
                smtp.send_message(msg)
        except Exception as exc:
            logger.exception("SMTP send failed template=%s", message.template_key)
            raise EmailDeliveryError(f"SMTP failure: {exc}") from exc
