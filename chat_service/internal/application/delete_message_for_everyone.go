package application

import (
	"context"
	"log/slog"
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type DeleteMessageForEveryoneCommand struct {
	MessageID string
	ActorID   string
}

type DeleteMessageForEveryoneResult struct {
	MessageID          string
	ConversationID     string
	DeletedForEveryone bool
}

type DeleteMessageForEveryoneHandler struct {
	uowFactory ports.UnitOfWorkFactory
	realtime   ports.RealtimeNotifier
	log        *slog.Logger
}

func NewDeleteMessageForEveryoneHandler(
	uowFactory ports.UnitOfWorkFactory,
	realtime ports.RealtimeNotifier,
	log *slog.Logger,
) *DeleteMessageForEveryoneHandler {
	return &DeleteMessageForEveryoneHandler{
		uowFactory: uowFactory,
		realtime:   realtime,
		log:        loggerOrDefault(log),
	}
}

func (h *DeleteMessageForEveryoneHandler) Handle(
	ctx context.Context,
	cmd DeleteMessageForEveryoneCommand,
) (DeleteMessageForEveryoneResult, error) {
	messageID, err := valueobjects.NewMessageID(cmd.MessageID)
	if err != nil {
		return DeleteMessageForEveryoneResult{}, err
	}
	actorID, err := valueobjects.NewUserID(cmd.ActorID)
	if err != nil {
		return DeleteMessageForEveryoneResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return DeleteMessageForEveryoneResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	msg, err := uow.Messages().GetByID(ctx, messageID)
	if err != nil {
		return DeleteMessageForEveryoneResult{}, err
	}
	if msg == nil {
		return DeleteMessageForEveryoneResult{}, &domainerrors.NotFoundError{
			Field:   "message_id",
			Message: "message " + messageID.String() + " not found",
		}
	}

	conv, err := loadConversationForParticipant(ctx, uow, msg.ConversationID, actorID)
	if err != nil {
		return DeleteMessageForEveryoneResult{}, err
	}

	if err := msg.DeleteForEveryone(actorID); err != nil {
		return DeleteMessageForEveryoneResult{}, err
	}
	if err := uow.Messages().Update(ctx, msg); err != nil {
		return DeleteMessageForEveryoneResult{}, err
	}

	// Refresh list preview only when this message is the cached last message.
	if conv.LastMessageID.Equals(msg.ID) {
		latest, err := uow.Messages().FindLatestVisible(ctx, msg.ConversationID)
		if err != nil {
			return DeleteMessageForEveryoneResult{}, err
		}
		if latest == nil {
			conv.ClearLastMessagePreview(time.Now().UTC())
		} else {
			conv.RecordLastMessage(*latest)
		}
		if err := uow.Conversations().Update(ctx, conv); err != nil {
			return DeleteMessageForEveryoneResult{}, err
		}
	}

	if err := uow.Commit(ctx); err != nil {
		return DeleteMessageForEveryoneResult{}, err
	}

	if counterpartID, ok := conv.CounterpartID(actorID); ok && h.realtime != nil {
		_ = h.realtime.NotifyUser(ctx, counterpartID.String(), map[string]any{
			"type":            "message_deleted",
			"conversation_id": msg.ConversationID.String(),
			"message_id":      msg.ID.String(),
		})
	}

	h.log.Info("message deleted for everyone",
		"message_id", msg.ID.String(),
		"conversation_id", msg.ConversationID.String(),
		"actor_id", actorID.String(),
	)

	return DeleteMessageForEveryoneResult{
		MessageID:          msg.ID.String(),
		ConversationID:     msg.ConversationID.String(),
		DeletedForEveryone: msg.DeletedForEveryone,
	}, nil
}
