package port

import (
	"context"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/event"
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

// UnitOfWork coordinates repository access and transactional boundaries.
type UnitOfWork interface {
	Conversations() ConversationRepository
	Commit(ctx context.Context) error
	Rollback(ctx context.Context) error
}

// UnitOfWorkFactory creates a new unit of work for a use case.
type UnitOfWorkFactory interface {
	New(ctx context.Context) (UnitOfWork, error)
}

// EventPublisher publishes integration events after successful commit.
type EventPublisher interface {
	Publish(ctx context.Context, evt event.DomainEvent) error
}

// RealtimeNotifier pushes live updates to connected participants (WebSocket).
type RealtimeNotifier interface {
	NotifyUser(ctx context.Context, userID string, payload any) error
}
