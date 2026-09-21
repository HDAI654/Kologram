package valueobject

import (
	"fmt"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
)

// UserID identifies a marketplace user (buyer or seller).
type UserID struct {
	value string
}

func NewUserID(raw string) (UserID, error) {
	id, err := parseUUIDv4(raw)
	if err != nil {
		return UserID{}, &domainerrors.ValidationError{
			Field:   "user_id",
			Message: fmt.Sprintf("invalid user id: %s", err),
		}
	}
	return UserID{value: id}, nil
}

func (id UserID) String() string { return id.value }

func (id UserID) Equals(other UserID) bool { return id.value == other.value }
