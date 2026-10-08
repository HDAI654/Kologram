package entities

import (
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// How long a sender may retract a message for everyone (WhatsApp-aligned).
const DeleteForEveryoneWindow = 60 * time.Hour

// Message is persisted independently of the Conversation aggregate.
// Soft-deleted messages (DeletedForEveryone) remain in storage for admin/security
// but are excluded from normal participant reads.
type Message struct {
	ID             valueobjects.MessageID
	ConversationID valueobjects.ConversationID
	SenderID       valueobjects.UserID
	Content        valueobjects.MessageContent
	SentAt         time.Time

	// Client-supplied idempotency key (UUID v4). Unique per (sender, conversation).
	ClientMessageID string

	DeletedForEveryone bool
	DeletedAt          *time.Time
}

// NewMessage requires a UUID v4 clientMessageID for retry deduplication.
func NewMessage(
	conversationID valueobjects.ConversationID,
	senderID valueobjects.UserID,
	clientMessageID string,
	content valueobjects.MessageContent,
) (Message, error) {
	if err := valueobjects.ValidateClientMessageID(clientMessageID); err != nil {
		return Message{}, err
	}
	return Message{
		ID:              valueobjects.GenerateMessageID(),
		ConversationID:  conversationID,
		SenderID:        senderID,
		Content:         content,
		SentAt:          time.Now().UTC(),
		ClientMessageID: clientMessageID,
	}, nil
}

// DeleteForEveryone soft-deletes the message for both participants.
// Only the sender may retract, only within the window (based on SentAt), and only once.
// Content is retained for admin/security; participant queries exclude this row.
func (m *Message) DeleteForEveryone(actorID valueobjects.UserID) error {
	if !m.SenderID.Equals(actorID) {
		return domainerrors.ErrNotMessageAuthor
	}
	if m.DeletedForEveryone {
		return nil
	}
	now := time.Now().UTC()
	if now.Sub(m.SentAt) > DeleteForEveryoneWindow {
		return domainerrors.ErrDeleteWindowExpired
	}
	m.DeletedForEveryone = true
	m.DeletedAt = &now
	return nil
}
