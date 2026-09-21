package ports

import "context"

// RealtimeNotifier pushes live updates to connected participants (WebSocket).
type RealtimeNotifier interface {
	NotifyUser(ctx context.Context, userID string, payload any) error
}
