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

// UserID identifies a marketplace user (buyer or seller).
type UserID struct {
	value string
}

func NewUserID(raw string) (UserID, error) {
	id, err := parseUUIDv4(raw)
	if err != nil {
		return UserID{}, fmt.Errorf("invalid user id: %w", err)
	}
	return UserID{value: id}, nil
}

func (id UserID) String() string { return id.value }

func (id UserID) Equals(other UserID) bool { return id.value == other.value }

// ListingID references the listing the conversation is about.
type ListingID struct {
	value string
}

func NewListingID(raw string) (ListingID, error) {
	id, err := parseUUIDv4(raw)
	if err != nil {
		return ListingID{}, fmt.Errorf("invalid listing id: %w", err)
	}
	return ListingID{value: id}, nil
}

func (id ListingID) String() string { return id.value }

func parseUUIDv4(raw string) (string, error) {
	if raw == "" {
		return "", fmt.Errorf("empty id")
	}
	parsed, err := uuid.Parse(raw)
	if err != nil {
		return "", err
	}
	if parsed.Version() != 4 {
		return "", fmt.Errorf("expected UUID v4")
	}
	return parsed.String(), nil
}
