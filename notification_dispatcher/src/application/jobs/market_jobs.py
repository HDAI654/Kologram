"""Notification jobs for market-service events."""

from __future__ import annotations

from src.application.jobs.base import NotificationJob, base_context, resolve_recipient
from src.conf import Config
from src.domain.events.envelope import IncomingEvent, require_fields
from src.domain.notifications.email_message import EmailMessage, NotificationSpec


class CategoryCreatedJob(NotificationJob):
    event_type = "CategoryCreated"

    def spec(self) -> NotificationSpec:
        return NotificationSpec(
            event_type=self.event_type,
            purpose="Operational notice that a category was created.",
            recipient_source="ADMIN_EMAIL (event has no user email)",
            subject_intent="Category created",
            required_context_keys=("category_id", "name", "occurred_at"),
            optional_context_keys=("parent_id",),
        )

    def build(self, event: IncomingEvent) -> EmailMessage:
        require_fields(event, "category_id", "name")
        to = resolve_recipient(
            event, admin_email=Config.ADMIN_EMAIL, allow_admin_fallback=True
        )
        return EmailMessage(
            to=to,
            subject_key="category_created",
            template_key="category_created",
            context=base_context(
                event,
                category_id=event.get("category_id"),
                name=event.get("name"),
                parent_id=event.get("parent_id"),
            ),
        )


class ListingCreatedJob(NotificationJob):
    event_type = "ListingCreated"

    def spec(self) -> NotificationSpec:
        return NotificationSpec(
            event_type=self.event_type,
            purpose="Notify seller that listing was created (draft/active per status).",
            recipient_source="event.email if present; else cannot deliver",
            subject_intent="Listing created",
            required_context_keys=("listing_id", "seller_id", "title", "occurred_at"),
            optional_context_keys=("category_id", "status", "email"),
        )

    def build(self, event: IncomingEvent) -> EmailMessage:
        require_fields(event, "listing_id", "seller_id", "title")
        to = resolve_recipient(event)
        return EmailMessage(
            to=to,
            subject_key="listing_created",
            template_key="listing_created",
            context=base_context(
                event,
                listing_id=event.get("listing_id"),
                seller_id=event.get("seller_id"),
                category_id=event.get("category_id"),
                title=event.get("title"),
                status=event.get("status"),
            ),
        )


class ListingDeletedJob(NotificationJob):
    event_type = "ListingDeleted"

    def spec(self) -> NotificationSpec:
        return NotificationSpec(
            event_type=self.event_type,
            purpose="Confirm listing deletion to the seller.",
            recipient_source="event.email if present",
            subject_intent="Listing deleted",
            required_context_keys=("listing_id", "seller_id", "occurred_at"),
            optional_context_keys=("email",),
        )

    def build(self, event: IncomingEvent) -> EmailMessage:
        require_fields(event, "listing_id", "seller_id")
        to = resolve_recipient(event)
        return EmailMessage(
            to=to,
            subject_key="listing_deleted",
            template_key="listing_deleted",
            context=base_context(
                event,
                listing_id=event.get("listing_id"),
                seller_id=event.get("seller_id"),
            ),
        )


class ListingPublishedJob(NotificationJob):
    event_type = "ListingPublished"

    def spec(self) -> NotificationSpec:
        return NotificationSpec(
            event_type=self.event_type,
            purpose="Notify seller listing is public/published.",
            recipient_source="event.email if present",
            subject_intent="Listing published",
            required_context_keys=("listing_id", "seller_id", "title", "occurred_at"),
            optional_context_keys=("category_id", "email"),
        )

    def build(self, event: IncomingEvent) -> EmailMessage:
        require_fields(event, "listing_id", "seller_id", "title")
        to = resolve_recipient(event)
        return EmailMessage(
            to=to,
            subject_key="listing_published",
            template_key="listing_published",
            context=base_context(
                event,
                listing_id=event.get("listing_id"),
                seller_id=event.get("seller_id"),
                category_id=event.get("category_id"),
                title=event.get("title"),
            ),
        )


class ListingStatusChangedJob(NotificationJob):
    event_type = "ListingStatusChanged"

    def spec(self) -> NotificationSpec:
        return NotificationSpec(
            event_type=self.event_type,
            purpose="Notify seller of listing status transition.",
            recipient_source="event.email if present",
            subject_intent="Listing status changed",
            required_context_keys=(
                "listing_id",
                "seller_id",
                "old_status",
                "new_status",
                "occurred_at",
            ),
            optional_context_keys=("email",),
        )

    def build(self, event: IncomingEvent) -> EmailMessage:
        require_fields(event, "listing_id", "seller_id", "old_status", "new_status")
        to = resolve_recipient(event)
        return EmailMessage(
            to=to,
            subject_key="listing_status_changed",
            template_key="listing_status_changed",
            context=base_context(
                event,
                listing_id=event.get("listing_id"),
                seller_id=event.get("seller_id"),
                old_status=event.get("old_status"),
                new_status=event.get("new_status"),
            ),
        )


class ListingUpdatedJob(NotificationJob):
    event_type = "ListingUpdated"

    def spec(self) -> NotificationSpec:
        return NotificationSpec(
            event_type=self.event_type,
            purpose="Notify seller that listing details were updated.",
            recipient_source="event.email if present",
            subject_intent="Listing updated",
            required_context_keys=("listing_id", "seller_id", "occurred_at"),
            optional_context_keys=("email",),
        )

    def build(self, event: IncomingEvent) -> EmailMessage:
        require_fields(event, "listing_id", "seller_id")
        to = resolve_recipient(event)
        return EmailMessage(
            to=to,
            subject_key="listing_updated",
            template_key="listing_updated",
            context=base_context(
                event,
                listing_id=event.get("listing_id"),
                seller_id=event.get("seller_id"),
            ),
        )
