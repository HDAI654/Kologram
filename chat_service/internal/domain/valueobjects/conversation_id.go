package valueobjects

import (
	"fmt"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/google/uuid"
)

// ConversationID is a UUID v4 identifier for a conversation aggregate.
type ConversationID struct {
	value string
}

func NewConversationID(raw string) (ConversationID, error) {
	id, err := parseUUIDv4(raw)
	if err != nil {
		return ConversationID{}, &domainerrors.ValidationError{
			Field:   "conversation_id",
			Message: fmt.Sprintf("invalid conversation id: %s", err),
		}
	}
	return ConversationID{value: id}, nil
}

func GenerateConversationID() ConversationID {
	return ConversationID{value: uuid.New().String()}
}

func (id ConversationID) String() string { return id.value }
