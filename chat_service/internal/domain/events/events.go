package events

import "time"

// DomainEvent is an immutable business fact published after a successful commit.
// Only events with a real cross-service consumer are defined here.
type DomainEvent interface {
	EventType() string
	OccurredAt() time.Time
}

// ConversationStarted — market/analytics: a buyer opened an inquiry on a listing.
type ConversationStarted struct {
	ConversationID string
	BuyerID        string
	SellerID       string
	ListingID      string
	At             time.Time
}

func (e ConversationStarted) EventType() string     { return "ConversationStarted" }
func (e ConversationStarted) OccurredAt() time.Time { return e.At }

// MessageSent — offline push / notification workers (WebSocket uses RealtimeNotifier).
// Payload is IDs only; consumers load body from chat storage if needed.
type MessageSent struct {
	ConversationID string
	MessageID      string
	SenderID       string
	RecipientID    string
	At             time.Time
}

func (e MessageSent) EventType() string     { return "MessageSent" }
func (e MessageSent) OccurredAt() time.Time { return e.At }
