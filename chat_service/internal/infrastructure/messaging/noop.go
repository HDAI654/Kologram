package messaging

import (
	"context"
	"log/slog"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/event"
)

// NoOpEventPublisher discards events (default when messaging is disabled).
type NoOpEventPublisher struct{}

func NewNoOpEventPublisher() *NoOpEventPublisher {
	return &NoOpEventPublisher{}
}

func (p *NoOpEventPublisher) Publish(_ context.Context, evt event.DomainEvent) error {
	slog.Debug("noop publish event", "type", evt.EventType())
	return nil
}
