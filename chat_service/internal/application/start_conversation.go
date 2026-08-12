package application

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/event"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/port"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

type StartConversationCommand struct {
	BuyerID   string
	SellerID  string
	ListingID string
}

type StartConversationResult struct {
	ConversationID string `json:"conversation_id"`
	Status         string `json:"status"`
	Created        bool   `json:"created"`
}

type StartConversationHandler struct {
	uowFactory port.UnitOfWorkFactory
	events     port.EventPublisher
}

func NewStartConversationHandler(
	uowFactory port.UnitOfWorkFactory,
	events port.EventPublisher,
) *StartConversationHandler {
	return &StartConversationHandler{uowFactory: uowFactory, events: events}
}

func (h *StartConversationHandler) Handle(
	ctx context.Context,
	cmd StartConversationCommand,
) (StartConversationResult, error) {
	buyerID, err := valueobject.NewUserID(cmd.BuyerID)
	if err != nil {
		return StartConversationResult{}, err
	}
	sellerID, err := valueobject.NewUserID(cmd.SellerID)
	if err != nil {
		return StartConversationResult{}, err
	}
	listingID, err := valueobject.NewListingID(cmd.ListingID)
	if err != nil {
		return StartConversationResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return StartConversationResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

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

	conversation, err := domain.StartConversation(buyerID, sellerID, listingID)
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
		_ = h.events.Publish(ctx, event.ConversationStarted{
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
