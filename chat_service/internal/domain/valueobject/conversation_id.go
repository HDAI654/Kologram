package valueobject

import (
	"fmt"

	"github.com/google/uuid"
)

// ConversationID is a UUID v4 identifier for a conversation aggregate.
type ConversationID struct {
	value string
}

func NewConversationID(raw string) (ConversationID, error) {
	id, err := parseUUIDv4(raw)
	if err != nil {
		return ConversationID{}, fmt.Errorf("invalid conversation id: %w", err)
	}
	return ConversationID{value: id}, nil
}

func GenerateConversationID() ConversationID {
	return ConversationID{value: uuid.New().String()}
}

func (id ConversationID) String() string { return id.value }
