package valueobject

import (
	"fmt"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/google/uuid"
)

// MessageID identifies a message within a conversation.
type MessageID struct {
	value string
}

func NewMessageID(raw string) (MessageID, error) {
	id, err := parseUUIDv4(raw)
	if err != nil {
		return MessageID{}, &domainerrors.ValidationError{
			Field:   "message_id",
			Message: fmt.Sprintf("invalid message id: %s", err),
		}
	}
	return MessageID{value: id}, nil
}

func GenerateMessageID() MessageID {
	return MessageID{value: uuid.New().String()}
}

func (id MessageID) String() string { return id.value }
