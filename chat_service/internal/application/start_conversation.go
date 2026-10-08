package application

import (
	"context"
	"log/slog"
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
	ConversationID string
	Created        bool
	IsReadOnly     bool
}

type StartConversationHandler struct {
	uowFactory  ports.UnitOfWorkFactory
	listingRepo ports.ListingRepository
	events      ports.EventPublisher
	log         *slog.Logger
}

func NewStartConversationHandler(
	uowFactory ports.UnitOfWorkFactory,
	listingRepo ports.ListingRepository,
	events ports.EventPublisher,
	log *slog.Logger,
) *StartConversationHandler {
	return &StartConversationHandler{
		uowFactory:  uowFactory,
		listingRepo: listingRepo,
		events:      events,
		log:         loggerOrDefault(log),
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

	listing, err := h.listingRepo.GetByID(ctx, listingID)
	if err != nil {
		return StartConversationResult{}, err
	}
	if listing == nil {
		return StartConversationResult{}, &domainerrors.NotFoundError{
			Field:   "listing_id",
			Message: "listing " + listingID.String() + " not found",
		}
	}
	if buyerID.Equals(listing.SellerID) {
		return StartConversationResult{}, domainerrors.ErrBuyerSellerSame
	}
	if !listing.MessageAllowed {
		return StartConversationResult{}, domainerrors.ErrListingNotMessageable
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return StartConversationResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	blocked, err := uow.UserBlocks().IsBlockedEitherWay(ctx, buyerID, listing.SellerID)
	if err != nil {
		return StartConversationResult{}, err
	}
	if blocked {
		return StartConversationResult{}, domainerrors.ErrUsersBlocked
	}

	existing, err := uow.Conversations().FindByBuyerAndListing(ctx, buyerID, listingID)
	if err != nil {
		return StartConversationResult{}, err
	}
	if existing != nil {
		return StartConversationResult{
			ConversationID: existing.ID.String(),
			Created:        false,
			IsReadOnly:     existing.IsReadOnly,
		}, nil
	}

	conversation, err := entities.StartConversation(buyerID, listing.SellerID, listingID)
	if err != nil {
		return StartConversationResult{}, err
	}

	now := time.Now().UTC()
	if err := uow.Conversations().Add(ctx, conversation); err != nil {
		return StartConversationResult{}, err
	}
	for _, uid := range conversation.ParticipantIDs() {
		state := entities.NewConversationUserState(conversation.ID, uid, now)
		if err := uow.ConversationStates().Add(ctx, state); err != nil {
			return StartConversationResult{}, err
		}
	}

	if err := uow.Commit(ctx); err != nil {
		return StartConversationResult{}, err
	}

	// Best-effort post-commit side effect (not transactional with the write).
	if h.events != nil {
		_ = h.events.Publish(ctx, events.ConversationStarted{
			ConversationID: conversation.ID.String(),
			BuyerID:        conversation.BuyerID.String(),
			SellerID:       conversation.SellerID.String(),
			ListingID:      conversation.ListingID.String(),
			At:             now,
		})
	}

	h.log.Info("conversation started",
		"conversation_id", conversation.ID.String(),
		"buyer_id", conversation.BuyerID.String(),
		"seller_id", conversation.SellerID.String(),
		"listing_id", conversation.ListingID.String(),
	)

	return StartConversationResult{
		ConversationID: conversation.ID.String(),
		Created:        true,
		IsReadOnly:     conversation.IsReadOnly,
	}, nil
}
