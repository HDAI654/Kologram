package ports

import (
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// ListingRepository check existence of listing by requesting market service
type ListingRepository interface {
	ExistByID(listing_id valueobjects.ListingID) (bool, error)
}
