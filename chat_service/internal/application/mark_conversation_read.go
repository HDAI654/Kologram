package application

import (
	"context"
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type MarkConversationReadCommand struct {
	ConversationID    string
	UserID            string
	LastReadMessageID string
}

type MarkConversationReadResult struct {
	ConversationID string
	UnreadCount    int
}

type MarkConversationReadHandler struct {
	uowFactory ports.UnitOfWorkFactory
}

func NewMarkConversationReadHandler(
	uowFactory ports.UnitOfWorkFactory,
) *MarkConversationReadHandler {
	return &MarkConversationReadHandler{uowFactory: uowFactory}
}

func (h *MarkConversationReadHandler) Handle(
	ctx context.Context,
	cmd MarkConversationReadCommand,
) (MarkConversationReadResult, error) {
	conversationID, err := valueobjects.NewConversationID(cmd.ConversationID)
	if err != nil {
		return MarkConversationReadResult{}, err
	}
	userID, err := valueobjects.NewUserID(cmd.UserID)
	if err != nil {
		return MarkConversationReadResult{}, err
	}
	lastReadID, err := valueobjects.NewMessageID(cmd.LastReadMessageID)
	if err != nil {
		return MarkConversationReadResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return MarkConversationReadResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	if _, err := loadConversationForParticipant(ctx, uow, conversationID, userID); err != nil {
		return MarkConversationReadResult{}, err
	}

	msg, err := uow.Messages().GetByID(ctx, lastReadID)
	if err != nil {
		return MarkConversationReadResult{}, err
	}
	if msg == nil || msg.DeletedForEveryone {
		return MarkConversationReadResult{}, &domainerrors.NotFoundError{
			Field:   "message_id",
			Message: "message " + lastReadID.String() + " not found",
		}
	}
	if msg.ConversationID.String() != conversationID.String() {
		return MarkConversationReadResult{}, &domainerrors.ValidationError{
			Field:   "last_read_message_id",
			Message: "message does not belong to this conversation",
		}
	}

	state, err := loadUserState(ctx, uow, conversationID, userID)
	if err != nil {
		return MarkConversationReadResult{}, err
	}

	now := time.Now().UTC()
	state.MarkRead(lastReadID, now)
	if err := uow.ConversationStates().Update(ctx, state); err != nil {
		return MarkConversationReadResult{}, err
	}
	if err := uow.Commit(ctx); err != nil {
		return MarkConversationReadResult{}, err
	}

	return MarkConversationReadResult{
		ConversationID: conversationID.String(),
		UnreadCount:    state.UnreadCount,
	}, nil
}
