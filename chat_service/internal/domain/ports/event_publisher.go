package ports

import (
	"context"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/events"
)

// Publishes integration events after a successful commit only.
type EventPublisher interface {
	Publish(ctx context.Context, evt events.DomainEvent) error
}
