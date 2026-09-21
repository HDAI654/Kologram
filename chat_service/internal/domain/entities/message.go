package domain

import (
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// Message is a child entity of the Conversation aggregate.
type Message struct {
	ID             valueobjects.MessageID
	ConversationID valueobjects.ConversationID
	SenderID       valueobjects.UserID
	Content        valueobjects.MessageContent
	IsRead         bool
	SentAt         time.Time
}

// NewMessage constructs a validated message.
func NewMessage(
	conversationID valueobjects.ConversationID,
	senderID valueobjects.UserID,
	content valueobjects.MessageContent,
) Message {
	return Message{
		ID:             valueobjects.GenerateMessageID(),
		ConversationID: conversationID,
		SenderID:       senderID,
		Content:        content,
		IsRead:         false,
		SentAt:         time.Now().UTC(),
	}
}

func (m *Message) MarkRead() {
	m.IsRead = true
}
