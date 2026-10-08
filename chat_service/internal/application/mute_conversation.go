package application

import (
	"context"
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type MuteConversationCommand struct {
	ConversationID string
	UserID         string
	// Mute=true requires Until (UTC). Mute=false clears mute.
	Mute  bool
	Until *time.Time
}

type MuteConversationResult struct {
	ConversationID string
	IsMuted        bool
	MutedUntil     *string
}

type MuteConversationHandler struct {
	uowFactory ports.UnitOfWorkFactory
}

func NewMuteConversationHandler(uowFactory ports.UnitOfWorkFactory) *MuteConversationHandler {
	return &MuteConversationHandler{uowFactory: uowFactory}
}

func (h *MuteConversationHandler) Handle(
	ctx context.Context,
	cmd MuteConversationCommand,
) (MuteConversationResult, error) {
	conversationID, err := valueobjects.NewConversationID(cmd.ConversationID)
	if err != nil {
		return MuteConversationResult{}, err
	}
	userID, err := valueobjects.NewUserID(cmd.UserID)
	if err != nil {
		return MuteConversationResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return MuteConversationResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	if _, err := loadConversationForParticipant(ctx, uow, conversationID, userID); err != nil {
		return MuteConversationResult{}, err
	}
	state, err := loadUserState(ctx, uow, conversationID, userID)
	if err != nil {
		return MuteConversationResult{}, err
	}

	now := time.Now().UTC()
	if cmd.Mute {
		if cmd.Until == nil || !cmd.Until.After(now) {
			return MuteConversationResult{}, &domainerrors.ValidationError{
				Field:   "muted_until",
				Message: "must be a future timestamp",
			}
		}
		state.Mute(cmd.Until.UTC(), now)
	} else {
		state.Unmute(now)
	}

	if err := uow.ConversationStates().Update(ctx, state); err != nil {
		return MuteConversationResult{}, err
	}
	if err := uow.Commit(ctx); err != nil {
		return MuteConversationResult{}, err
	}

	result := MuteConversationResult{
		ConversationID: conversationID.String(),
		IsMuted:        state.IsMuted(now),
	}
	if state.MutedUntil != nil {
		s := state.MutedUntil.Format(time.RFC3339)
		result.MutedUntil = &s
	}
	return result, nil
}
