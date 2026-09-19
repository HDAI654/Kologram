package valueobject

import (
	"fmt"

	"github.com/google/uuid"
)

// MessageID identifies a message within a conversation.
type MessageID struct {
	value string
}

func NewMessageID(raw string) (MessageID, error) {
	id, err := parseUUIDv4(raw)
	if err != nil {
		return MessageID{}, fmt.Errorf("invalid message id: %w", err)
	}
	return MessageID{value: id}, nil
}

func GenerateMessageID() MessageID {
	return MessageID{value: uuid.New().String()}
}

func (id MessageID) String() string { return id.value }
