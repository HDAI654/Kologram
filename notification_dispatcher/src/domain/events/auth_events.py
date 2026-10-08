"""Trusted auth event payloads (no domain validation)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserRegistered:
    user_id: str
    email: str
    occurred_at: str | None = None


@dataclass(frozen=True, slots=True)
class UserLoggedIn:
    user_id: str
    email: str
    session_id: str
    device: str
    occurred_at: str | None = None


@dataclass(frozen=True, slots=True)
class UserLoggedOut:
    user_id: str
    session_id: str
    device: str
    email: str = ""
    occurred_at: str | None = None


@dataclass(frozen=True, slots=True)
class AccountDeleted:
    user_id: str
    occurred_at: str | None = None


@dataclass(frozen=True, slots=True)
class VerificationTokenCreated:
    token: str
    email: str
    token_type: str
    occurred_at: str | None = None
