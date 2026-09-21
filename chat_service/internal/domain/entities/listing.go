package entities

import (
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type Listing struct {
	ID             valueobjects.ListingID
	SellerID       valueobjects.UserID
	MessageAllowed bool
}
