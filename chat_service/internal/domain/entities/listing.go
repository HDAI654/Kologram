package entities

import (
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// Listing is a read-only projection of the market-service listing.
// Used only to resolve seller and messageability when starting a conversation.
type Listing struct {
	ID             valueobjects.ListingID
	SellerID       valueobjects.UserID
	MessageAllowed bool
}
