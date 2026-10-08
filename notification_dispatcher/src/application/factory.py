"""Wire jobs + dispatcher from config."""

from __future__ import annotations

from src.application.dispatcher import Dispatcher
from src.application.jobs.auth_jobs import (
    AccountDeletedJob,
    ResetPasswordTokenJob,
    UserLoggedInJob,
    UserLoggedOutJob,
    UserRegisteredJob,
    VerifyEmailTokenJob,
)
from src.application.jobs.chat_jobs import ConversationStartedJob, MessageSentJob
from src.application.jobs.market_jobs import (
    CategoryCreatedJob,
    ListingCreatedJob,
    ListingDeletedJob,
    ListingPublishedJob,
    ListingStatusChangedJob,
    ListingUpdatedJob,
)
from src.conf import Config
from src.domain.ports.email_sender import EmailSender
from src.domain.ports.idempotency_store import IdempotencyStore
from src.infrastructure.email.console_sender import ConsoleEmailSender
from src.infrastructure.email.smtp_sender import SmtpEmailSender


def build_email_sender() -> EmailSender:
    if Config.EMAIL_ENABLED:
        return SmtpEmailSender(
            host=Config.SMTP_HOST,
            port=Config.SMTP_PORT,
            user=Config.SMTP_USER,
            password=Config.SMTP_PASSWORD,
            from_addr=Config.EMAIL_FROM,
            use_tls=Config.SMTP_USE_TLS,
            use_ssl=Config.SMTP_USE_SSL,
        )
    return ConsoleEmailSender()


def build_dispatcher(email_sender: EmailSender, idempotency: IdempotencyStore) -> Dispatcher:
    attempts = Config.EMAIL_MAX_ATTEMPTS
    jobs = {
        "UserRegistered": UserRegisteredJob(email_sender, attempts),
        "UserLoggedIn": UserLoggedInJob(email_sender, attempts),
        "UserLoggedOut": UserLoggedOutJob(email_sender, attempts),
        "AccountDeleted": AccountDeletedJob(),
        "CategoryCreated": CategoryCreatedJob(),
        "ListingCreated": ListingCreatedJob(),
        "ListingPublished": ListingPublishedJob(),
        "ListingStatusChanged": ListingStatusChangedJob(),
        "ListingUpdated": ListingUpdatedJob(),
        "ListingDeleted": ListingDeletedJob(),
        "ConversationStarted": ConversationStartedJob(),
        "MessageSent": MessageSentJob(),
    }
    verification_jobs = {
        "verifyemail": VerifyEmailTokenJob(email_sender, attempts),
        "forget_pass_verify": ResetPasswordTokenJob(email_sender, attempts),
    }
    return Dispatcher(jobs, idempotency, verification_jobs=verification_jobs)
