package ports

import (
	"context"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// ListingRepository check existence of listing by requesting market service
type ListingRepository interface {
	GetByID(ctx context.Context, listing_id valueobjects.ListingID) (*entities.Listing, error)
}
