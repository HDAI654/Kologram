package domainerrors

import (
	"errors"
	"fmt"
)

var (
	// ErrInvalidArgument indicates a value object or argument failed validation.
	ErrInvalidArgument = errors.New("invalid argument")

	// ErrNotFound indicates a requested aggregate or resource does not exist.
	ErrNotFound = errors.New("not found")

	// ErrAlreadyExists indicates a uniqueness constraint would be violated.
	ErrAlreadyExists = errors.New("already exists")

	// ErrConflict indicates a domain state conflict.
	ErrConflict = errors.New("conflict")

	// ErrForbidden indicates the caller is not permitted to perform the action.
	ErrForbidden = errors.New("forbidden")
)

// ---------------------------------------------------------------------------
// Typed validation errors (Value Objects)
// ---------------------------------------------------------------------------

// ValidationError is raised when a value object invariant is violated.
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

// ---------------------------------------------------------------------------
// Typed not found errors (entities)
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Specific domain rules — each wraps its category.
// ---------------------------------------------------------------------------

var (
	// ErrBuyerSellerSame is a cross-field rule: buyer and seller must differ.
	ErrBuyerSellerSame = fmt.Errorf(
		"buyer and seller must be different: %w",
		ErrInvalidArgument,
	)

	// ErrNotParticipant is returned when the caller is not a party to the conversation.
	ErrNotParticipant = fmt.Errorf(
		"user is not a participant of this conversation: %w",
		ErrForbidden,
	)

	// ErrConversationNotOpen is returned when a message is sent to
	// a conversation whose status does not allow new messages.
	ErrConversationNotOpen = fmt.Errorf(
		"conversation is not open for new messages: %w",
		ErrConflict,
	)

	// ErrInvalidStatusTransition is returned when the requested status change is
	// not permitted from the conversation's current status.
	ErrInvalidStatusTransition = fmt.Errorf(
		"invalid conversation status transition: %w",
		ErrConflict,
	)

	// ErrListingNotMessageable is returned when a listing does not allow new conversations.
	ErrListingNotMessageable = fmt.Errorf(
		"listing does not allow new conversations: %w",
		ErrConflict,
	)
)
