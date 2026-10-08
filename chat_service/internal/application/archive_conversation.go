package application

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type ArchiveConversationCommand struct {
	ConversationID string
	UserID         string
	Archive        bool // true = archive, false = unarchive
}

type ArchiveConversationResult struct {
	ConversationID string
	IsArchived     bool
}

type ArchiveConversationHandler struct {
	uowFactory ports.UnitOfWorkFactory
}

func NewArchiveConversationHandler(uowFactory ports.UnitOfWorkFactory) *ArchiveConversationHandler {
	return &ArchiveConversationHandler{uowFactory: uowFactory}
}

func (h *ArchiveConversationHandler) Handle(
	ctx context.Context,
	cmd ArchiveConversationCommand,
) (ArchiveConversationResult, error) {
	conversationID, err := valueobjects.NewConversationID(cmd.ConversationID)
	if err != nil {
		return ArchiveConversationResult{}, err
	}
	userID, err := valueobjects.NewUserID(cmd.UserID)
	if err != nil {
		return ArchiveConversationResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return ArchiveConversationResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	if _, err := loadConversationForParticipant(ctx, uow, conversationID, userID); err != nil {
		return ArchiveConversationResult{}, err
	}
	state, err := loadUserState(ctx, uow, conversationID, userID)
	if err != nil {
		return ArchiveConversationResult{}, err
	}

	now := time.Now().UTC()
	if cmd.Archive {
		state.Archive(now)
	} else {
		state.Unarchive(now)
	}
	if err := uow.ConversationStates().Update(ctx, state); err != nil {
		return ArchiveConversationResult{}, err
	}
	if err := uow.Commit(ctx); err != nil {
		return ArchiveConversationResult{}, err
	}

	return ArchiveConversationResult{
		ConversationID: conversationID.String(),
		IsArchived:     state.IsArchived,
	}, nil
}
