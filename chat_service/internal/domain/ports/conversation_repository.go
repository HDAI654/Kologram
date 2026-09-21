package ports

import (
	"context"

	domain "github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

// ConversationRepository loads and saves conversation aggregates.
type ConversationRepository interface {
	Add(ctx context.Context, conversation *domain.Conversation) error
	GetByID(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error)
	Update(ctx context.Context, conversation *domain.Conversation) error
	FindByBuyerAndListing(
		ctx context.Context,
		buyerID valueobject.UserID,
		listingID valueobject.ListingID,
	) (*domain.Conversation, error)
	ListForUser(
		ctx context.Context,
		userID valueobject.UserID,
		limit, offset int,
	) ([]*domain.Conversation, error)
}
