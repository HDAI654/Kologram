package ports

import "context"

// Connected-client push (WebSocket). Not a domain event and not durable.
// Callers skip notify when the recipient's conversation is muted.
type RealtimeNotifier interface {
	NotifyUser(ctx context.Context, userID string, payload any) error
}
