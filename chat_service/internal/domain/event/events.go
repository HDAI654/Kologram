package event

import "time"

// DomainEvent is published after a successful commit.
type DomainEvent interface {
	EventType() string
	OccurredAt() time.Time
}

type ConversationStarted struct {
	ConversationID string
	BuyerID        string
	SellerID       string
	ListingID      string
	At             time.Time
}

func (e ConversationStarted) EventType() string   { return "ConversationStarted" }
func (e ConversationStarted) OccurredAt() time.Time { return e.At }

type MessageSent struct {
	ConversationID string
	MessageID      string
	SenderID       string
	Content        string
	At             time.Time
}

func (e MessageSent) EventType() string   { return "MessageSent" }
func (e MessageSent) OccurredAt() time.Time { return e.At }

type ConversationStatusChanged struct {
	ConversationID string
	OldStatus      string
	NewStatus      string
	ActorID        string
	At             time.Time
}

func (e ConversationStatusChanged) EventType() string   { return "ConversationStatusChanged" }
func (e ConversationStatusChanged) OccurredAt() time.Time { return e.At }

type MessagesRead struct {
	ConversationID string
	ReaderID       string
	At             time.Time
}

func (e MessagesRead) EventType() string   { return "MessagesRead" }
func (e MessagesRead) OccurredAt() time.Time { return e.At }
