package ports

import (
	"context"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// Blocks are global to the user pair, not conversation-scoped.
type UserBlockRepository interface {
	// Duplicate insert may be treated as a no-op.
	Add(ctx context.Context, block *entities.UserBlock) error

	// Removing a nonexistent block is a no-op.
	Remove(
		ctx context.Context,
		blockerID valueobjects.UserID,
		blockedID valueobjects.UserID,
	) error

	Exists(
		ctx context.Context,
		blockerID valueobjects.UserID,
		blockedID valueobjects.UserID,
	) (bool, error)

	// StartConversation and SendMessage require this to be false.
	IsBlockedEitherWay(
		ctx context.Context,
		userA valueobjects.UserID,
		userB valueobjects.UserID,
	) (bool, error)
}
