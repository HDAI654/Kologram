package valueobjects

import (
	"fmt"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
)

// ValidateClientMessageID ensures the idempotency key is a UUID v4.
func ValidateClientMessageID(raw string) error {
	if raw == "" {
		return &domainerrors.ValidationError{
			Field:   "client_message_id",
			Message: "must not be empty",
		}
	}
	if _, err := parseUUIDv4(raw); err != nil {
		return &domainerrors.ValidationError{
			Field:   "client_message_id",
			Message: fmt.Sprintf("must be a UUID v4: %s", err),
		}
	}
	return nil
}
