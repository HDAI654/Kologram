package application

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/event"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/port"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

type ChangeStatusCommand struct {
	ConversationID string
	ActorID        string
	NewStatus      string
}

type ChangeStatusResult struct {
	ConversationID string `json:"conversation_id"`
	Status         string `json:"status"`
}

type ChangeStatusHandler struct {
	uowFactory port.UnitOfWorkFactory
	events     port.EventPublisher
}

func NewChangeStatusHandler(
	uowFactory port.UnitOfWorkFactory,
	events port.EventPublisher,
) *ChangeStatusHandler {
	return &ChangeStatusHandler{uowFactory: uowFactory, events: events}
}

func (h *ChangeStatusHandler) Handle(
	ctx context.Context,
	cmd ChangeStatusCommand,
) (ChangeStatusResult, error) {
	conversationID, err := valueobject.NewConversationID(cmd.ConversationID)
	if err != nil {
		return ChangeStatusResult{}, err
	}
	actorID, err := valueobject.NewUserID(cmd.ActorID)
	if err != nil {
		return ChangeStatusResult{}, err
	}
	target, err := valueobject.NewConversationStatus(cmd.NewStatus)
	if err != nil {
		return ChangeStatusResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return ChangeStatusResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	conversation, err := uow.Conversations().GetByID(ctx, conversationID)
	if err != nil {
		return ChangeStatusResult{}, err
	}
	oldStatus := conversation.Status.String()
	if err := conversation.TransitionStatus(target, actorID); err != nil {
		return ChangeStatusResult{}, err
	}
	if err := uow.Conversations().Update(ctx, conversation); err != nil {
		return ChangeStatusResult{}, err
	}
	if err := uow.Commit(ctx); err != nil {
		return ChangeStatusResult{}, err
	}

	if h.events != nil {
		_ = h.events.Publish(ctx, event.ConversationStatusChanged{
			ConversationID: conversation.ID.String(),
			OldStatus:      oldStatus,
			NewStatus:      conversation.Status.String(),
			ActorID:        actorID.String(),
			At:             time.Now().UTC(),
		})
	}

	return ChangeStatusResult{
		ConversationID: conversation.ID.String(),
		Status:         conversation.Status.String(),
	}, nil
}
