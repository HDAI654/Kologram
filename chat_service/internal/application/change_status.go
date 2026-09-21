package application

import (
	"context"
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/events"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
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
	uowFactory ports.UnitOfWorkFactory
	events     ports.EventPublisher
}

func NewChangeStatusHandler(
	uowFactory ports.UnitOfWorkFactory,
	events ports.EventPublisher,
) *ChangeStatusHandler {
	return &ChangeStatusHandler{uowFactory: uowFactory, events: events}
}

func (h *ChangeStatusHandler) Handle(
	ctx context.Context,
	cmd ChangeStatusCommand,
) (ChangeStatusResult, error) {
	conversationID, err := valueobjects.NewConversationID(cmd.ConversationID)
	if err != nil {
		return ChangeStatusResult{}, err
	}
	actorID, err := valueobjects.NewUserID(cmd.ActorID)
	if err != nil {
		return ChangeStatusResult{}, err
	}
	target, err := valueobjects.NewConversationStatus(cmd.NewStatus)
	if err != nil {
		return ChangeStatusResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return ChangeStatusResult{}, err
	}

	// No-op after a successful commit; rolls back on any other exit.
	defer func() { _ = uow.Rollback(ctx) }()

	conversation, err := uow.Conversations().GetByID(ctx, conversationID)
	if err != nil {
		return ChangeStatusResult{}, err
	}
	if conversation == nil {
		return ChangeStatusResult{}, &domainerrors.NotFoundError{
			Field:   "conversation_id",
			Message: "conversation " + conversationID.String() + " not found",
		}
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
		_ = h.events.Publish(ctx, events.ConversationStatusChanged{
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
