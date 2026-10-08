package entities

import (
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// UserBlock records that one user has blocked another.
// Not conversation-scoped — a block affects every interaction between the pair.
type UserBlock struct {
	BlockerID valueobjects.UserID
	BlockedID valueobjects.UserID
	BlockedAt time.Time
}

func NewUserBlock(
	blocker valueobjects.UserID,
	blocked valueobjects.UserID,
) (*UserBlock, error) {
	if blocker.Equals(blocked) {
		return nil, domainerrors.ErrCannotBlockSelf
	}
	return &UserBlock{
		BlockerID: blocker,
		BlockedID: blocked,
		BlockedAt: time.Now().UTC(),
	}, nil
}
