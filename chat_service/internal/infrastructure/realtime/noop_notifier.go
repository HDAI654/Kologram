package realtime

import (
	"context"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
)

// NoOpNotifier is a placeholder until Presentation wires a real WebSocket hub.
type NoOpNotifier struct{}

func NewNoOpNotifier() *NoOpNotifier { return &NoOpNotifier{} }

func (NoOpNotifier) NotifyUser(ctx context.Context, userID string, payload any) error {
	return nil
}

var _ ports.RealtimeNotifier = NoOpNotifier{}
