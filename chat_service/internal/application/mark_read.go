package application

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/event"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/port"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

type MarkReadCommand struct {
	ConversationID string
	ReaderID       string
}

type MarkReadResult struct {
	ConversationID string `json:"conversation_id"`
}

type MarkReadHandler struct {
	uowFactory port.UnitOfWorkFactory
	events     port.EventPublisher
	realtime   port.RealtimeNotifier
}

func NewMarkReadHandler(
	uowFactory port.UnitOfWorkFactory,
	events port.EventPublisher,
	realtime port.RealtimeNotifier,
) *MarkReadHandler {
	return &MarkReadHandler{uowFactory: uowFactory, events: events, realtime: realtime}
}

func (h *MarkReadHandler) Handle(ctx context.Context, cmd MarkReadCommand) (MarkReadResult, error) {
	conversationID, err := valueobject.NewConversationID(cmd.ConversationID)
	if err != nil {
		return MarkReadResult{}, err
	}
	readerID, err := valueobject.NewUserID(cmd.ReaderID)
	if err != nil {
		return MarkReadResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return MarkReadResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	conversation, err := uow.Conversations().GetByID(ctx, conversationID)
	if err != nil {
		return MarkReadResult{}, err
	}
	if err := conversation.MarkMessagesRead(readerID); err != nil {
		return MarkReadResult{}, err
	}
	if err := uow.Conversations().Update(ctx, conversation); err != nil {
		return MarkReadResult{}, err
	}
	if err := uow.Commit(ctx); err != nil {
		return MarkReadResult{}, err
	}

	if h.realtime != nil {
		payload := map[string]any{
			"type":            "messages.read",
			"conversation_id": conversation.ID.String(),
			"reader_id":       readerID.String(),
		}
		_ = h.realtime.NotifyUser(ctx, conversation.BuyerID.String(), payload)
		_ = h.realtime.NotifyUser(ctx, conversation.SellerID.String(), payload)
	}

	if h.events != nil {
		_ = h.events.Publish(ctx, event.MessagesRead{
			ConversationID: conversation.ID.String(),
			ReaderID:       readerID.String(),
			At:             time.Now().UTC(),
		})
	}

	return MarkReadResult{ConversationID: conversation.ID.String()}, nil
}
