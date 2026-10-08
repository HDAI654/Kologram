package application

import (
	"context"
	"log/slog"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// System use case: market service reports a listing deleted/unavailable.
type MarkListingUnavailableCommand struct {
	ListingID string
}

type MarkListingUnavailableResult struct {
	ListingID          string
	ConversationsFrozen int
}

type MarkListingUnavailableHandler struct {
	uowFactory ports.UnitOfWorkFactory
	log        *slog.Logger
}

func NewMarkListingUnavailableHandler(
	uowFactory ports.UnitOfWorkFactory,
	log *slog.Logger,
) *MarkListingUnavailableHandler {
	return &MarkListingUnavailableHandler{
		uowFactory: uowFactory,
		log:        loggerOrDefault(log),
	}
}

func (h *MarkListingUnavailableHandler) Handle(
	ctx context.Context,
	cmd MarkListingUnavailableCommand,
) (MarkListingUnavailableResult, error) {
	listingID, err := valueobjects.NewListingID(cmd.ListingID)
	if err != nil {
		return MarkListingUnavailableResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return MarkListingUnavailableResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	conversations, err := uow.Conversations().ListByListingID(ctx, listingID)
	if err != nil {
		return MarkListingUnavailableResult{}, err
	}

	now := time.Now().UTC()
	frozen := 0
	for _, conv := range conversations {
		if conv.IsReadOnly {
			continue
		}
		conv.MarkListingUnavailable(now)
		if err := uow.Conversations().Update(ctx, conv); err != nil {
			return MarkListingUnavailableResult{}, err
		}
		frozen++
	}

	if err := uow.Commit(ctx); err != nil {
		return MarkListingUnavailableResult{}, err
	}

	h.log.Info("listing marked unavailable",
		"listing_id", listingID.String(),
		"conversations_frozen", frozen,
	)

	return MarkListingUnavailableResult{
		ListingID:           listingID.String(),
		ConversationsFrozen: frozen,
	}, nil
}
