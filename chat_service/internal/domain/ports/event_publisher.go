package ports

import (
	"context"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/events"
)

// EventPublisher publishes integration events after successful commit.
type EventPublisher interface {
	Publish(ctx context.Context, evt events.DomainEvent) error
}
