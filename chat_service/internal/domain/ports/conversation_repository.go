package ports

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// ConversationCursor anchors a page in a user's conversation list.
// Sort key is (LastMessageAt DESC, ID DESC).
type ConversationCursor struct {
	LastMessageAt time.Time
	ID            valueobjects.ConversationID
}

// ConversationRepository persists and loads conversation aggregates.
type ConversationRepository interface {
	Add(ctx context.Context, conversation *entities.Conversation) error

	Update(ctx context.Context, conversation *entities.Conversation) error

	// Delete soft-deletes the conversation. Subsequent reads do not return it.
	Delete(ctx context.Context, id valueobjects.ConversationID) error

	// GetByID returns the conversation. Implementations must return a
	// NotFoundError when no row exists.
	GetByID(ctx context.Context, id valueobjects.ConversationID) (*entities.Conversation, error)

	// FindByBuyerAndListing returns (nil, nil) when no conversation exists.
	FindByBuyerAndListing(
		ctx context.Context,
		buyerID valueobjects.UserID,
		listingID valueobjects.ListingID,
	) (*entities.Conversation, error)

	// ListForUser returns a page of conversations the user participates in,
	// ordered by most recent activity. A nil cursor starts from the newest.
	ListForUser(
		ctx context.Context,
		userID valueobjects.UserID,
		cursor *ConversationCursor,
		limit int,
	) ([]*entities.Conversation, error)
}
