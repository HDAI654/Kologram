package domainerrors

import (
	"errors"
	"fmt"
)

var (
	ErrInvalidArgument = errors.New("invalid argument")
	ErrNotFound        = errors.New("not found")
	ErrAlreadyExists   = errors.New("already exists")
	ErrConflict        = errors.New("conflict")
	ErrForbidden       = errors.New("forbidden")
)

// ValidationError is raised when a value-object invariant is violated.
type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string {
	if e.Field == "" {
		return e.Message
	}
	return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

func (e *ValidationError) Unwrap() error {
	return ErrInvalidArgument
}

// NotFoundError is raised when a requested entity does not exist.
type NotFoundError struct {
	Field   string
	Message string
}

func (e *NotFoundError) Error() string {
	if e.Field == "" {
		return e.Message
	}
	return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

func (e *NotFoundError) Unwrap() error {
	return ErrNotFound
}

// Domain rule violations — each wraps its category sentinel.
var (
	ErrBuyerSellerSame = fmt.Errorf(
		"buyer and seller must be different: %w",
		ErrInvalidArgument,
	)

	ErrNotParticipant = fmt.Errorf(
		"user is not a participant of this conversation: %w",
		ErrForbidden,
	)

	ErrConversationNotOpen = fmt.Errorf(
		"conversation is not open for new messages: %w",
		ErrConflict,
	)

	ErrListingNotMessageable = fmt.Errorf(
		"listing does not allow new conversations: %w",
		ErrConflict,
	)

	ErrNotMessageAuthor = fmt.Errorf(
		"only the sender may retract this message: %w",
		ErrForbidden,
	)

	ErrDeleteWindowExpired = fmt.Errorf(
		"message retraction window has expired: %w",
		ErrConflict,
	)

	ErrCannotBlockSelf = fmt.Errorf(
		"cannot block yourself: %w",
		ErrInvalidArgument,
	)

	// Either user has blocked the other — start/send must fail.
	ErrUsersBlocked = fmt.Errorf(
		"users are blocked from interacting: %w",
		ErrForbidden,
	)
)
