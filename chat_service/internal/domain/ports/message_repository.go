package ports

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// MessageCursor anchors a page in a conversation's message history.
// Sort key is (SentAt, ID) — both are required to break timestamp ties.
type MessageCursor struct {
	SentAt time.Time
	ID     valueobjects.MessageID
}

// Direction selects which side of the cursor to walk.
type Direction int

const (
	// DirectionOlder walks backward in history (scroll up).
	DirectionOlder Direction = iota
	// DirectionNewer walks forward in time (sync new messages).
	DirectionNewer
)

// MessageRepository loads and saves messages.
type MessageRepository interface {
	Add(ctx context.Context, message *entities.Message) error

	// Delete soft-deletes the message. Subsequent reads do not return it.
	Delete(ctx context.Context, message_id valueobjects.MessageID) error

	Update(ctx context.Context, message *entities.Message) error

	// ListMessages returns a page of messages in a conversation.
	//
	// DirectionOlder:
	//   nil cursor   → newest page, returned newest-first
	//   given cursor → messages older than the cursor, newest-first
	//
	// DirectionNewer:
	//   given cursor → messages newer than the cursor, oldest-first
	ListMessages(
		ctx context.Context,
		conversationID valueobjects.ConversationID,
		cursor *MessageCursor,
		direction Direction,
		limit int,
	) ([]*entities.Message, error)

	// CountNewMessagesInConversation returns the number of messages newer
	// than the cursor. The cursor is typically the last message the caller
	// has seen.
	CountNewMessagesInConversation(
		ctx context.Context,
		conversationID valueobjects.ConversationID,
		cursor *MessageCursor,
	) (int64, error)
}
