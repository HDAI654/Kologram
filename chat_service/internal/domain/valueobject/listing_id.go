package valueobject

import (
	"fmt"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
)

// ListingID references the listing the conversation is about.
type ListingID struct {
	value string
}

func NewListingID(raw string) (ListingID, error) {
	id, err := parseUUIDv4(raw)
	if err != nil {
		return ListingID{}, &domainerrors.ValidationError{
			Field:   "listing_id",
			Message: fmt.Sprintf("invalid listing id: %s", err),
		}
	}
	return ListingID{value: id}, nil
}

func (id ListingID) String() string { return id.value }
