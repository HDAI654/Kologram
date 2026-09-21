package domain

import (
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

// Message is a child entity of the Conversation aggregate.
type Message struct {
	ID             valueobject.MessageID
	ConversationID valueobject.ConversationID
	SenderID       valueobject.UserID
	Content        valueobject.MessageContent
	IsRead         bool
	SentAt         time.Time
}

// NewMessage constructs a validated message.
func NewMessage(
	conversationID valueobject.ConversationID,
	senderID valueobject.UserID,
	content valueobject.MessageContent,
) Message {
	return Message{
		ID:             valueobject.GenerateMessageID(),
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
