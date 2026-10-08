package application

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type HideConversationCommand struct {
	ConversationID string
	UserID         string
	Hide           bool // true = hide, false = unhide
}

type HideConversationResult struct {
	ConversationID string
	IsHidden       bool
}

type HideConversationHandler struct {
	uowFactory ports.UnitOfWorkFactory
}

func NewHideConversationHandler(uowFactory ports.UnitOfWorkFactory) *HideConversationHandler {
	return &HideConversationHandler{uowFactory: uowFactory}
}

func (h *HideConversationHandler) Handle(
	ctx context.Context,
	cmd HideConversationCommand,
) (HideConversationResult, error) {
	conversationID, err := valueobjects.NewConversationID(cmd.ConversationID)
	if err != nil {
		return HideConversationResult{}, err
	}
	userID, err := valueobjects.NewUserID(cmd.UserID)
	if err != nil {
		return HideConversationResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return HideConversationResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	if _, err := loadConversationForParticipant(ctx, uow, conversationID, userID); err != nil {
		return HideConversationResult{}, err
	}
	state, err := loadUserState(ctx, uow, conversationID, userID)
	if err != nil {
		return HideConversationResult{}, err
	}

	now := time.Now().UTC()
	if cmd.Hide {
		state.Hide(now)
	} else {
		state.Unhide(now)
	}
	if err := uow.ConversationStates().Update(ctx, state); err != nil {
		return HideConversationResult{}, err
	}
	if err := uow.Commit(ctx); err != nil {
		return HideConversationResult{}, err
	}

	return HideConversationResult{
		ConversationID: conversationID.String(),
		IsHidden:       state.IsHidden,
	}, nil
}
