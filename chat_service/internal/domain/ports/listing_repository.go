package ports

import (
	"context"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// Market-service adapter: existence, seller, and messageability.
// Not part of the chat UnitOfWork (external system).
type ListingRepository interface {
	// Returns (nil, nil) when the listing does not exist.
	GetByID(ctx context.Context, listingID valueobjects.ListingID) (*entities.Listing, error)
}
