"""Market event jobs — temporary NOTHING."""

from __future__ import annotations

import logging
from typing import Any

from src.application.jobs.base import NotificationJob

logger = logging.getLogger(__name__)


class CategoryCreatedJob(NotificationJob):
    event_type = "CategoryCreated"

    def handle(self, payload: dict[str, Any]) -> None:
        # Temporary NOTHING: no notification until product requires category ops alerts.
        logger.info("CategoryCreated temporary NOTHING payload_keys=%s", list(payload.keys()))


class ListingCreatedJob(NotificationJob):
    event_type = "ListingCreated"

    def handle(self, payload: dict[str, Any]) -> None:
        # Temporary NOTHING: no notification for draft/create.
        logger.info("ListingCreated temporary NOTHING payload_keys=%s", list(payload.keys()))


class ListingPublishedJob(NotificationJob):
    event_type = "ListingPublished"

    def handle(self, payload: dict[str, Any]) -> None:
        # Temporary NOTHING: publish alerts deferred.
        logger.info("ListingPublished temporary NOTHING payload_keys=%s", list(payload.keys()))


class ListingStatusChangedJob(NotificationJob):
    event_type = "ListingStatusChanged"

    def handle(self, payload: dict[str, Any]) -> None:
        # Temporary NOTHING: status change emails deferred.
        logger.info(
            "ListingStatusChanged temporary NOTHING payload_keys=%s", list(payload.keys())
        )


class ListingUpdatedJob(NotificationJob):
    event_type = "ListingUpdated"

    def handle(self, payload: dict[str, Any]) -> None:
        # Temporary NOTHING: update notifications deferred.
        logger.info("ListingUpdated temporary NOTHING payload_keys=%s", list(payload.keys()))


class ListingDeletedJob(NotificationJob):
    event_type = "ListingDeleted"

    def handle(self, payload: dict[str, Any]) -> None:
        # Temporary NOTHING: deletion notifications deferred.
        logger.info("ListingDeleted temporary NOTHING payload_keys=%s", list(payload.keys()))
