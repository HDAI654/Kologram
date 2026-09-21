package application

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/events"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type StartConversationCommand struct {
	BuyerID   string
	ListingID string
}

type StartConversationResult struct {
	ConversationID string `json:"conversation_id"`
	Status         string `json:"status"`
	Created        bool   `json:"created"`
}

type StartConversationHandler struct {
	uowFactory   ports.UnitOfWorkFactory
	listing_repo ports.ListingRepository
	events       ports.EventPublisher
}

func NewStartConversationHandler(
	uowFactory ports.UnitOfWorkFactory,
	listing_repo ports.ListingRepository,
	events ports.EventPublisher,
) *StartConversationHandler {
	return &StartConversationHandler{
		uowFactory:   uowFactory,
		listing_repo: listing_repo,
		events:       events,
	}
}

func (h *StartConversationHandler) Handle(
	ctx context.Context,
	cmd StartConversationCommand,
) (StartConversationResult, error) {

	buyerID, err := valueobjects.NewUserID(cmd.BuyerID)
	if err != nil {
		return StartConversationResult{}, err
	}
	listingID, err := valueobjects.NewListingID(cmd.ListingID)
	if err != nil {
		return StartConversationResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return StartConversationResult{}, err
	}

	// No-op after a successful commit; rolls back on any other exit.
	defer func() { _ = uow.Rollback(ctx) }()

	// Idempotent: return the existing conversation if one already exists.
	existing, err := uow.Conversations().FindByBuyerAndListing(ctx, buyerID, listingID)
	if err != nil {
		return StartConversationResult{}, err
	}
	if existing != nil {
		return StartConversationResult{
			ConversationID: existing.ID.String(),
			Status:         existing.Status.String(),
			Created:        false,
		}, nil
	}

	// Seller is derived from the listing, not the request.
	listing, err := h.listing_repo.GetByID(listingID)
	if err != nil {
		return StartConversationResult{}, err
	}
	if listing == nil {
		return StartConversationResult{}, &domainerrors.NotFoundError{
			Field:   "listing_id",
			Message: "listing " + listingID.String() + " not found",
		}
	}

	// Buyer cannot start a conversation with themselves.
	if buyerID.Equals(listing.SellerID) {
		return StartConversationResult{}, domainerrors.ErrBuyerSellerSame
	}

	conversation, err := entities.StartConversation(buyerID, listing.SellerID, listingID)
	if err != nil {
		return StartConversationResult{}, err
	}

	if err := uow.Conversations().Add(ctx, conversation); err != nil {
		return StartConversationResult{}, err
	}
	if err := uow.Commit(ctx); err != nil {
		return StartConversationResult{}, err
	}

	if h.events != nil {
		_ = h.events.Publish(ctx, events.ConversationStarted{
			ConversationID: conversation.ID.String(),
			BuyerID:        conversation.BuyerID.String(),
			SellerID:       conversation.SellerID.String(),
			ListingID:      conversation.ListingID.String(),
			At:             time.Now().UTC(),
		})
	}

	return StartConversationResult{
		ConversationID: conversation.ID.String(),
		Status:         conversation.Status.String(),
		Created:        true,
	}, nil
}
