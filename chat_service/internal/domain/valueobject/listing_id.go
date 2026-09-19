package valueobject

import (
	"fmt"
)

// ListingID references the listing the conversation is about.
type ListingID struct {
	value string
}

func NewListingID(raw string) (ListingID, error) {
	id, err := parseUUIDv4(raw)
	if err != nil {
		return ListingID{}, fmt.Errorf("invalid listing id: %w", err)
	}
	return ListingID{value: id}, nil
}

func (id ListingID) String() string { return id.value }
