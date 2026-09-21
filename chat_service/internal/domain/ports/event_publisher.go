package ports

import "context"

// EventPublisher publishes integration events after successful commit.
type EventPublisher interface {
	Publish(ctx context.Context, evt event.DomainEvent) error
}
