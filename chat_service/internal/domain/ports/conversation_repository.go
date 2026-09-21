package ports

import (
	"context"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// ConversationRepository loads and saves conversation aggregates.
type ConversationRepository interface {
	Add(ctx context.Context, conversation *entities.Conversation) error
	Delete(ctx context.Context, conversation_id valueobjects.ConversationID) error
	GetByID(ctx context.Context, id valueobjects.ConversationID) (*entities.Conversation, error)
	Update(ctx context.Context, conversation *entities.Conversation) error
	AddMessage(ctx context.Context, conversation_id valueobjects.ConversationID, message *entities.Message) error
	FindByBuyerAndListing(
		ctx context.Context,
		buyerID valueobjects.UserID,
		listingID valueobjects.ListingID,
	) (*entities.Conversation, error)

	// ListForUser returns the user's conversations, each with only its most
	// recent message populated, plus the total conversation count for pagination.
	ListForUser(
		ctx context.Context,
		userID valueobjects.UserID,
		limit, offset int,
	) ([]*entities.Conversation, int32, error)
}
