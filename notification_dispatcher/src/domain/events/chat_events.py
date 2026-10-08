"""Trusted chat event payloads (temporary NOTHING handlers)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConversationStarted:
    conversation_id: str = ""
    buyer_id: str = ""
    seller_id: str = ""
    listing_id: str = ""
    occurred_at: str | None = None


@dataclass(frozen=True, slots=True)
class MessageSent:
    conversation_id: str = ""
    message_id: str = ""
    sender_id: str = ""
    recipient_id: str = ""
    occurred_at: str | None = None
