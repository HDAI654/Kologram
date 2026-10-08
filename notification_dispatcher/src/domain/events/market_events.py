"""Trusted market event payloads (temporary NOTHING handlers)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CategoryCreated:
    category_id: str = ""
    name: str = ""
    occurred_at: str | None = None


@dataclass(frozen=True, slots=True)
class ListingCreated:
    listing_id: str = ""
    seller_id: str = ""
    occurred_at: str | None = None


@dataclass(frozen=True, slots=True)
class ListingPublished:
    listing_id: str = ""
    seller_id: str = ""
    category_id: str = ""
    title: str = ""
    occurred_at: str | None = None


@dataclass(frozen=True, slots=True)
class ListingStatusChanged:
    listing_id: str = ""
    seller_id: str = ""
    old_status: str = ""
    new_status: str = ""
    occurred_at: str | None = None


@dataclass(frozen=True, slots=True)
class ListingUpdated:
    listing_id: str = ""
    seller_id: str = ""
    occurred_at: str | None = None


@dataclass(frozen=True, slots=True)
class ListingDeleted:
    listing_id: str = ""
    seller_id: str = ""
    occurred_at: str | None = None
