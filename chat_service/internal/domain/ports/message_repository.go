package ports

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// Sort key: (SentAt, ID) — both required to break timestamp ties.
type MessageCursor struct {
	SentAt time.Time
	ID     valueobjects.MessageID
}

type Direction int

const (
	DirectionOlder Direction = iota // scroll up / history
	DirectionNewer                  // sync after reconnect
)

type MessageRepository interface {
	Add(ctx context.Context, message *entities.Message) error

	// Used for DeleteForEveryone (flag + DeletedAt).
	Update(ctx context.Context, message *entities.Message) error

	// Must return NotFoundError when no row exists.
	// Returns soft-deleted messages (admin/internal paths may need them).
	GetByID(ctx context.Context, id valueobjects.MessageID) (*entities.Message, error)

	// Returns (nil, nil) when no match — SendMessage idempotency.
	// Includes soft-deleted rows so retries still resolve to the same message.
	FindByClientMessageID(
		ctx context.Context,
		senderID valueobjects.UserID,
		conversationID valueobjects.ConversationID,
		clientMessageID string,
	) (*entities.Message, error)

	// Latest non-deleted message in the conversation.
	// Returns (nil, nil) when none remain visible.
	// Used to refresh LastMessagePreview after DeleteForEveryone.
	FindLatestVisible(
		ctx context.Context,
		conversationID valueobjects.ConversationID,
	) (*entities.Message, error)

	// Participant history: soft-deleted messages are excluded.
	//
	// DirectionOlder:
	//   nil cursor   → newest page, newest-first
	//   given cursor → older than cursor, newest-first
	// DirectionNewer:
	//   given cursor → newer than cursor, oldest-first
	ListMessages(
		ctx context.Context,
		conversationID valueobjects.ConversationID,
		cursor *MessageCursor,
		direction Direction,
		limit int,
	) ([]*entities.Message, error)
}
