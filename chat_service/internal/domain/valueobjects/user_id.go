package valueobject

import (
	"fmt"
)

// UserID identifies a marketplace user (buyer or seller).
type UserID struct {
	value string
}

func NewUserID(raw string) (UserID, error) {
	id, err := parseUUIDv4(raw)
	if err != nil {
		return UserID{}, fmt.Errorf("invalid user id: %w", err)
	}
	return UserID{value: id}, nil
}

func (id UserID) String() string { return id.value }

func (id UserID) Equals(other UserID) bool { return id.value == other.value }
