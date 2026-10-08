package application

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type PinConversationCommand struct {
	ConversationID string
	UserID         string
	Pin            bool // true = pin, false = unpin
}

type PinConversationResult struct {
	ConversationID string
	IsPinned       bool
}

type PinConversationHandler struct {
	uowFactory ports.UnitOfWorkFactory
}

func NewPinConversationHandler(uowFactory ports.UnitOfWorkFactory) *PinConversationHandler {
	return &PinConversationHandler{uowFactory: uowFactory}
}

func (h *PinConversationHandler) Handle(
	ctx context.Context,
	cmd PinConversationCommand,
) (PinConversationResult, error) {
	conversationID, err := valueobjects.NewConversationID(cmd.ConversationID)
	if err != nil {
		return PinConversationResult{}, err
	}
	userID, err := valueobjects.NewUserID(cmd.UserID)
	if err != nil {
		return PinConversationResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return PinConversationResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	if _, err := loadConversationForParticipant(ctx, uow, conversationID, userID); err != nil {
		return PinConversationResult{}, err
	}
	state, err := loadUserState(ctx, uow, conversationID, userID)
	if err != nil {
		return PinConversationResult{}, err
	}

	now := time.Now().UTC()
	if cmd.Pin {
		state.Pin(now)
	} else {
		state.Unpin(now)
	}
	if err := uow.ConversationStates().Update(ctx, state); err != nil {
		return PinConversationResult{}, err
	}
	if err := uow.Commit(ctx); err != nil {
		return PinConversationResult{}, err
	}

	return PinConversationResult{
		ConversationID: conversationID.String(),
		IsPinned:       state.IsPinned,
	}, nil
}
