package ports

import (
	"context"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// One row per (conversation, user).
type ConversationUserStateRepository interface {
	Add(ctx context.Context, state *entities.ConversationUserState) error

	// Must not regress LastReadMessageID — an older cursor must not overwrite a newer one.
	Update(ctx context.Context, state *entities.ConversationUserState) error

	// Must return NotFoundError when no row exists.
	Get(
		ctx context.Context,
		conversationID valueobjects.ConversationID,
		userID valueobjects.UserID,
	) (*entities.ConversationUserState, error)

	// Both participants' rows in one round-trip (SendMessage: bump receiver
	// unread, optionally unhide receiver; leave sender unread unchanged).
	ListForConversation(
		ctx context.Context,
		conversationID valueobjects.ConversationID,
	) ([]*entities.ConversationUserState, error)
}
